from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: Optional[str] = Field(default=None, index=True, unique=True)
    kind: str = Field(index=True)
    prompt: str
    status: str = Field(default="queued", index=True)
    filename: Optional[str] = None
    full_path: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    finished_at: Optional[datetime] = None
    meta_json: Optional[str] = None
