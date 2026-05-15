from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    id: int | None = None
    timestamp: datetime
    node: str
    agent: str
    type: str
    content: str
    tags: list[str] = Field(default_factory=list)
    session_id: str | None = None
