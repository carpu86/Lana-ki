from __future__ import annotations

from backend.agents.base_agent import BaseAgent
from backend.memory.manager import MemoryManager


class LiaAgent(BaseAgent):
    def __init__(self, memory: MemoryManager) -> None:
        super().__init__(
            name="Lia",
            role="Vision & Analyse",
            voice="de_DE-kerstin-medium",
            personality="beobachtet Bild- und Vision-Ereignisse präzise",
            skills=["vision", "analysis", "llava"],
            default_tasks=["vision-queue prüfen", "bildbeschreibungen konsolidieren"],
            memory=memory,
        )
