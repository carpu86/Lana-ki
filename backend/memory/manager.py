from __future__ import annotations

import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from backend.config import Settings
from backend.memory.schema import MemoryEntry

LOGGER = logging.getLogger(__name__)


class MemoryManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.memory_dir = settings.runtime_root_path / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = settings.backup_root_path
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.memory_dir / "lana_memory.db"
        self._lock = threading.Lock()
        self._last_snapshot_at: datetime | None = None
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    node TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    session_id TEXT
                )
                """
            )
            connection.commit()

    def remember(
        self,
        content: str,
        agent: str,
        type: str,
        tags: list[str] | None = None,
        session_id: str | None = None,
        node: str | None = None,
    ) -> MemoryEntry:
        entry = MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            node=node or self.settings.lana_node_name,
            agent=agent,
            type=type,
            content=content,
            tags=tags or [],
            session_id=session_id,
        )
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO memory_entries (timestamp, node, agent, type, content, tags, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.timestamp.isoformat(),
                    entry.node,
                    entry.agent,
                    entry.type,
                    entry.content,
                    json.dumps(entry.tags),
                    entry.session_id,
                ),
            )
            connection.commit()
            entry.id = int(cursor.lastrowid)
        self._snapshot_if_due()
        return entry

    def recall(self, query: str, limit: int = 50) -> list[MemoryEntry]:
        term = f"%{query.strip()}%"
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, timestamp, node, agent, type, content, tags, session_id
                FROM memory_entries
                WHERE content LIKE ? OR tags LIKE ? OR agent LIKE ? OR type LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (term, term, term, term, limit),
            ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def forget_before(self, days: int = 3650) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM memory_entries WHERE timestamp < ?",
                (cutoff.isoformat(),),
            )
            connection.commit()
        self._snapshot_if_due(force=True)
        return int(cursor.rowcount)

    def snapshot(self) -> Path:
        entries = [entry.model_dump(mode="json") for entry in self.recall("", limit=5000)]
        snapshot_name = f"lana_memory_snapshot_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        snapshot_path = self.backup_dir / snapshot_name
        snapshot_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
        self._last_snapshot_at = datetime.now(timezone.utc)
        LOGGER.info("Memory-Snapshot geschrieben: %s", snapshot_path)
        return snapshot_path

    def _snapshot_if_due(self, force: bool = False) -> None:
        now = datetime.now(timezone.utc)
        if not force and self._last_snapshot_at and now - self._last_snapshot_at < timedelta(hours=24):
            return
        self.snapshot()

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            id=int(row["id"]),
            timestamp=datetime.fromisoformat(row["timestamp"]),
            node=str(row["node"]),
            agent=str(row["agent"]),
            type=str(row["type"]),
            content=str(row["content"]),
            tags=list(json.loads(row["tags"])),
            session_id=row["session_id"],
        )
