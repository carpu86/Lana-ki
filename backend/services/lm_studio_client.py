from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)


class LMStudioClient:
    """OpenAI-kompatibler Client für LM Studio (kein Ollama)."""

    def __init__(self) -> None:
        self.base_url = os.getenv("LANA_LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
        self.model = os.getenv("LANA_LMSTUDIO_MODEL", "qwen2.5-7b-instruct")

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def embeddings(self, text: str, model: str = "text-embedding-nomic-embed-text-v1.5") -> list[float]:
        payload = {"model": model, "input": text}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return data["data"][0]["embedding"]

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/models")
                return resp.status_code == 200
        except Exception:
            return False
