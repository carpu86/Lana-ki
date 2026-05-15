from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class RouterResult:
    content: str
    provider: str
    tokens_used: int


class IntentRouter:
    """Wählt automatisch den richtigen LLM-Provider (LM Studio → Azure → Gemini → Groq → OpenAI)."""

    TIMEOUT = 10.0

    def __init__(self) -> None:
        self._lmstudio_base = os.getenv("LANA_LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
        self._lmstudio_model = os.getenv("LANA_LMSTUDIO_MODEL", "qwen2.5-7b-instruct")

        self._azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self._azure_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self._azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
        self._azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

        self._gemini_key = os.getenv("GEMINI_API_KEY", "")
        self._gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        self._groq_key = os.getenv("GROQ_API_KEY", "")
        self._openai_key = os.getenv("OPENAI_API_KEY", "")

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> RouterResult:
        for attempt in (
            self._try_lm_studio,
            self._try_azure,
            self._try_gemini,
            self._try_groq,
            self._try_openai,
        ):
            try:
                result = await attempt(messages, temperature, max_tokens)
                if result is not None:
                    return result
            except Exception as exc:
                logger.warning("[intent_router] %s failed: %s", attempt.__name__, exc)

        raise RuntimeError("Alle LLM-Provider nicht erreichbar.")

    async def _try_lm_studio(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> RouterResult | None:
        payload = {
            "model": self._lmstudio_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            resp = await client.post(
                f"{self._lmstudio_base}/chat/completions",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        logger.info("[intent_router] provider=lm_studio tokens=%d", tokens)
        return RouterResult(content=content, provider="lm_studio", tokens_used=tokens)

    async def _try_azure(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> RouterResult | None:
        if not self._azure_key or not self._azure_endpoint or not self._azure_deployment:
            return None
        url = (
            f"{self._azure_endpoint.rstrip('/')}/openai/deployments/"
            f"{self._azure_deployment}/chat/completions"
            f"?api-version={self._azure_api_version}"
        )
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"api-key": self._azure_key},
            )
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        logger.info("[intent_router] provider=azure tokens=%d", tokens)
        return RouterResult(content=content, provider="azure", tokens_used=tokens)

    async def _try_gemini(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> RouterResult | None:
        if not self._gemini_key:
            return None
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._gemini_model}:generateContent?key={self._gemini_key}"
        )
        parts = [{"text": m["content"]} for m in messages if m.get("role") != "system"]
        system_parts = [m["content"] for m in messages if m.get("role") == "system"]
        body: dict = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_parts:
            body["systemInstruction"] = {"parts": [{"text": " ".join(system_parts)}]}
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
        logger.info("[intent_router] provider=gemini tokens=%d", tokens)
        return RouterResult(content=content, provider="gemini", tokens_used=tokens)

    async def _try_groq(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> RouterResult | None:
        if not self._groq_key:
            return None
        payload = {
            "model": "llama3-70b-8192",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self._groq_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        logger.info("[intent_router] provider=groq tokens=%d", tokens)
        return RouterResult(content=content, provider="groq", tokens_used=tokens)

    async def _try_openai(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> RouterResult | None:
        if not self._openai_key:
            return None
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self._openai_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        logger.info("[intent_router] provider=openai tokens=%d", tokens)
        return RouterResult(content=content, provider="openai", tokens_used=tokens)
