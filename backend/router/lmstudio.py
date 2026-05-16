from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.config import Settings

LOGGER = logging.getLogger(__name__)


class LMStudioClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.settings.lana_lmstudio_url}/v1/models")
                response.raise_for_status()
            return True
        except httpx.HTTPError:
            LOGGER.warning("LM Studio nicht erreichbar unter %s", self.settings.lana_lmstudio_url)
            return False

    async def chat(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        payload = {
            "model": "qwen2.5-7b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt or "Du bist Lana, die Core-Orchestratorin."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self.settings.lana_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.lana_lmstudio_url}/v1/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        reply = message.get("content", "")
        return {"provider": "lmstudio", "reply": reply, "raw": body}
