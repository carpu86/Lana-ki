from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http import models as qmodels

    _QDRANT_AVAILABLE = True
except ImportError:
    _QDRANT_AVAILABLE = False
    logger.warning("qdrant-client not installed — LanaMemory running in no-op mode.")

from backend.memory.character_store import CharacterSheet
from backend.services.lm_studio_client import LMStudioClient

_VECTOR_SIZE = 768  # nomic-embed-text-v1.5


@dataclass
class MemoryEntry:
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class LanaMemory:
    """Qdrant-basiertes Langzeit-Gedächtnis pro User + Girl."""

    collection_prefix = "lana_"

    def __init__(self) -> None:
        self._url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self._embedder = LMStudioClient()
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if not _QDRANT_AVAILABLE:
            return None
        if self._client is None:
            self._client = AsyncQdrantClient(url=self._url)
        return self._client

    def _col(self, user_id: str, girl_id: str) -> str:
        return f"{self.collection_prefix}{user_id}_{girl_id}_messages"

    def _char_col(self, user_id: str, girl_id: str) -> str:
        return f"{self.collection_prefix}{user_id}_{girl_id}_character"

    async def _ensure_collection(self, name: str) -> None:
        client = self._get_client()
        if client is None:
            return
        try:
            await client.get_collection(name)
        except Exception:
            await client.create_collection(
                collection_name=name,
                vectors_config=qmodels.VectorParams(
                    size=_VECTOR_SIZE,
                    distance=qmodels.Distance.COSINE,
                ),
            )

    async def store_message(
        self,
        user_id: str,
        girl_id: str,
        role: str,
        content: str,
        metadata: dict,
    ) -> None:
        client = self._get_client()
        if client is None:
            return
        col = self._col(user_id, girl_id)
        await self._ensure_collection(col)
        try:
            vector = await self._embedder.embeddings(content)
        except Exception as exc:
            logger.warning("Embedding failed, using zero vector: %s", exc)
            vector = [0.0] * _VECTOR_SIZE

        import uuid
        point_id = str(uuid.uuid4())
        payload = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            **metadata,
        }
        await client.upsert(
            collection_name=col,
            points=[
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    async def search_relevant(
        self,
        user_id: str,
        girl_id: str,
        query: str,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        client = self._get_client()
        if client is None:
            return []
        col = self._col(user_id, girl_id)
        await self._ensure_collection(col)
        try:
            vector = await self._embedder.embeddings(query)
        except Exception:
            return []
        results = await client.search(
            collection_name=col,
            query_vector=vector,
            limit=limit,
        )
        return [
            MemoryEntry(
                role=r.payload.get("role", "user"),
                content=r.payload.get("content", ""),
                timestamp=r.payload.get("timestamp", 0.0),
                metadata={k: v for k, v in r.payload.items() if k not in ("role", "content", "timestamp")},
            )
            for r in results
        ]

    async def get_recent(
        self,
        user_id: str,
        girl_id: str,
        n: int = 20,
    ) -> list[MemoryEntry]:
        client = self._get_client()
        if client is None:
            return []
        col = self._col(user_id, girl_id)
        await self._ensure_collection(col)
        try:
            results, _ = await client.scroll(
                collection_name=col,
                limit=n,
                with_payload=True,
                with_vectors=False,
                order_by=qmodels.OrderBy(
                    key="timestamp",
                    direction=qmodels.Direction.Desc,
                ),
            )
        except Exception:
            results, _ = await client.scroll(
                collection_name=col,
                limit=n,
                with_payload=True,
                with_vectors=False,
            )
        entries = [
            MemoryEntry(
                role=r.payload.get("role", "user"),
                content=r.payload.get("content", ""),
                timestamp=r.payload.get("timestamp", 0.0),
            )
            for r in results
        ]
        return list(reversed(entries))

    async def store_character(
        self,
        user_id: str,
        girl_id: str,
        character_sheet: CharacterSheet,
    ) -> None:
        client = self._get_client()
        if client is None:
            return
        col = self._char_col(user_id, girl_id)
        await self._ensure_collection(col)
        import uuid
        point_id = str(uuid.uuid4())
        await client.upsert(
            collection_name=col,
            points=[
                qmodels.PointStruct(
                    id=point_id,
                    vector=[0.0] * _VECTOR_SIZE,
                    payload=character_sheet.to_dict(),
                )
            ],
        )

    async def get_character(
        self,
        user_id: str,
        girl_id: str,
    ) -> CharacterSheet | None:
        client = self._get_client()
        if client is None:
            return None
        col = self._char_col(user_id, girl_id)
        await self._ensure_collection(col)
        try:
            results, _ = await client.scroll(
                collection_name=col,
                limit=1,
                with_payload=True,
                with_vectors=False,
            )
            if results:
                return CharacterSheet.from_dict(results[0].payload)
        except Exception as exc:
            logger.warning("get_character failed: %s", exc)
        return None
