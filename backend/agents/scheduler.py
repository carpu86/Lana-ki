from __future__ import annotations

import asyncio
import logging
import threading
import time
from collections import deque
from typing import Any

import schedule

from backend.agents.base_agent import BaseAgent
from backend.agents.lana import LanaAgent
from backend.agents.lia import LiaAgent
from backend.mcp.tools import MCPToolRegistry
from backend.memory.manager import MemoryManager

LOGGER = logging.getLogger(__name__)


class AutonomousScheduler:
    def __init__(self, memory: MemoryManager, tool_registry: MCPToolRegistry, interval_seconds: int = 60) -> None:
        self.memory = memory
        self.tool_registry = tool_registry
        self.interval_seconds = interval_seconds
        self.events: deque[str] = deque(maxlen=100)
        self.chat_timelines: dict[str, list[str]] = {}
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.agents = self._build_agents()
        schedule.clear("lana-autonomous")
        schedule.every(self.interval_seconds).seconds.do(self._run_cycle).tag("lana-autonomous")

    def _build_agents(self) -> list[BaseAgent]:
        shell_executor = self.tool_registry.execute_shell_on_node if self.tool_registry.context.settings.enable_autonomous_shell else None
        return [
            LanaAgent(self.memory, shell_executor=shell_executor),
            LiaAgent(self.memory),
            BaseAgent(
                name="Mia",
                role="Daten & Memory",
                voice="de_DE-thorsten-medium",
                personality="strukturiert, archiviert langfristiges Wissen",
                skills=["memory", "sqlite", "snapshots"],
                default_tasks=["memory-konsistenz prüfen", "snapshot-plan aktualisieren"],
                memory=self.memory,
            ),
            BaseAgent(
                name="Sophie",
                role="UI & Frontend",
                voice="de_DE-kerstin-medium",
                personality="achtet auf UX und Frontend-Flows",
                skills=["ui", "frontend", "web"],
                default_tasks=["frontend-status spiegeln", "component-ideen notieren"],
                memory=self.memory,
            ),
            BaseAgent(
                name="Chloe",
                role="Telegram & Social",
                voice="de_DE-kerstin-medium",
                personality="kommunikativ, bot-zentriert",
                skills=["telegram", "social", "notifications"],
                default_tasks=["telegram-status prüfen", "social-events vormerken"],
                memory=self.memory,
            ),
            BaseAgent(
                name="Emma",
                role="Planung & Scheduling",
                voice="de_DE-thorsten-medium",
                personality="plant vorausschauend und taktet autonome Jobs",
                skills=["planning", "schedule", "ops"],
                default_tasks=["tagesplan erstellen", "wartungsfenster bewerten"],
                memory=self.memory,
            ),
        ]

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_forever, name="lana-scheduler", daemon=True)
        self._thread.start()
        LOGGER.info("Autonomer Scheduler gestartet.")

    def stop(self) -> None:
        self._stop_event.set()
        schedule.clear("lana-autonomous")
        if self._thread:
            self._thread.join(timeout=5)
        LOGGER.info("Autonomer Scheduler gestoppt.")

    def publish_event(self, event: str) -> None:
        self.events.append(event)
        self.memory.remember(event, agent="scheduler", type="event", tags=["queued"])

    def status(self) -> dict[str, Any]:
        return {
            "running": bool(self._thread and self._thread.is_alive()),
            "interval_seconds": self.interval_seconds,
            "queued_events": len(self.events),
            "agents": [agent.name for agent in self.agents],
            "chat_timelines": self.chat_timelines,
        }

    def _run_forever(self) -> None:
        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    def _run_cycle(self) -> None:
        asyncio.run(self._run_cycle_async())

    async def _run_cycle_async(self) -> None:
        pending_events = list(self.events)
        self.events.clear()
        for event in pending_events:
            for agent in self.agents:
                reaction = await agent.react_to_event(event)
                self.chat_timelines.setdefault(agent.name, []).append(reaction)
        for agent in self.agents:
            results = await agent.run_default_cycle()
            self.chat_timelines.setdefault(agent.name, []).extend(results)
