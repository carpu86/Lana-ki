from __future__ import annotations

from typing import Any

import httpx

from backend.config import Settings


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def chat(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        api_key = self.settings.resolve_secret(self.settings.gemini_api_key_ref)
        if not api_key:
            raise RuntimeError(f"Gemini-Key aus Referenz {self.settings.gemini_api_key_ref!r} fehlt.")
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.lana_gemini_model}:generateContent"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt or "Du bist Lana."}]},
            "contents": [{"parts": [{"text": prompt}]}],
        }
        params = {"key": api_key}
        async with httpx.AsyncClient(timeout=self.settings.lana_timeout_seconds) as client:
            response = await client.post(endpoint, params=params, json=payload)
            response.raise_for_status()
            body = response.json()
        candidates = body.get("candidates") or [{}]
        parts = ((candidates[0].get("content") or {}).get("parts") or [{}])
        reply = parts[0].get("text", "")
        return {"provider": "gemini", "reply": reply, "raw": body}
