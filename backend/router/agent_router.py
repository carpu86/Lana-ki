from __future__ import annotations

import logging
from typing import Any

import httpx
from pydantic import BaseModel, Field

from backend.config import Settings
from backend.router.gemini import GeminiClient
from backend.router.lmstudio import LMStudioClient

LOGGER = logging.getLogger(__name__)


class ChatRouteResult(BaseModel):
    provider: str
    reply: str
    attempts: list[dict[str, Any]] = Field(default_factory=list)


class AgentRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.lmstudio = LMStudioClient(settings)
        self.gemini = GeminiClient(settings)

    async def route_chat(self, prompt: str, system_prompt: str | None = None) -> ChatRouteResult:
        attempts: list[dict[str, Any]] = []
        for provider in ("local", "gemini", "openai"):
            try:
                if provider == "local":
                    result = await self.lmstudio.chat(prompt, system_prompt=system_prompt)
                elif provider == "gemini":
                    result = await self.gemini.chat(prompt, system_prompt=system_prompt)
                else:
                    result = await self._chat_openai(prompt, system_prompt=system_prompt)
                attempts.append({"provider": provider, "status": "ok"})
                return ChatRouteResult(
                    provider=str(result["provider"]),
                    reply=str(result["reply"]),
                    attempts=attempts,
                )
            except Exception as exc:
                LOGGER.warning("Routing-Stufe %s fehlgeschlagen: %s", provider, exc)
                attempts.append({"provider": provider, "status": "error", "detail": str(exc)})
        raise RuntimeError(f"Kein Modell verfügbar. Details: {attempts}")

    async def _chat_openai(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        api_key = self.settings.resolve_secret(self.settings.openai_api_key_ref)
        if not api_key:
            raise RuntimeError(f"OpenAI-Key aus Referenz {self.settings.openai_api_key_ref!r} fehlt.")
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt or "Du bist Lana."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        async with httpx.AsyncClient(timeout=self.settings.lana_timeout_seconds) as client:
            response = await client.post(self.settings.openai_base_url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        reply = message.get("content", "")
        return {"provider": "openai", "reply": reply, "raw": body}
