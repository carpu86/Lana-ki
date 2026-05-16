from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Awaitable, Callable

from backend.memory.manager import MemoryManager

LOGGER = logging.getLogger(__name__)
ShellExecutor = Callable[[str, str], Awaitable[dict[str, object]]]


@dataclass(slots=True)
class BaseAgent:
    name: str
    role: str
    voice: str
    personality: str
    skills: list[str]
    default_tasks: list[str]
    memory: MemoryManager
    shell_executor: ShellExecutor | None = None
    conversation_log: list[str] = field(default_factory=list)

    async def react_to_event(self, event: str) -> str:
        reply = f"{self.name} reagiert auf Ereignis: {event}"
        self.conversation_log.append(reply)
        self.memory.remember(reply, agent=self.name, type="event", tags=["scheduler", "event"])
        LOGGER.info(reply)
        return reply

    async def run_default_cycle(self) -> list[str]:
        results: list[str] = []
        for task in self.default_tasks:
            if task.startswith("shell:") and self.shell_executor:
                _, node, command = task.split(":", 2)
                shell_result = await self.shell_executor(node, command)
                summary = f"{self.name} Shell {node}: {shell_result.get('returncode', 'n/a')}"
                results.append(summary)
                self.memory.remember(
                    str(shell_result),
                    agent=self.name,
                    type="shell",
                    tags=["scheduler", node],
                )
            else:
                summary = f"{self.name} bearbeitet: {task}"
                results.append(summary)
                self.memory.remember(summary, agent=self.name, type="task", tags=["scheduler"])
            self.conversation_log.append(results[-1])
            LOGGER.info(results[-1])
        return results
