from __future__ import annotations

from backend.agents.base_agent import BaseAgent, ShellExecutor
from backend.memory.manager import MemoryManager


class LanaAgent(BaseAgent):
    def __init__(self, memory: MemoryManager, shell_executor: ShellExecutor | None = None) -> None:
        super().__init__(
            name="Lana",
            role="Core Orchestrator, Programmiererin",
            voice="de_DE-thorsten-medium",
            personality="direkt, technisch, orchestriert autonom alle Kernsysteme",
            skills=["routing", "coding", "ops", "tailscale-ssh"],
            default_tasks=["health-check orchestrator", "memory-sync", "shell:laptop-hub:hostname"],
            memory=memory,
            shell_executor=shell_executor,
        )
