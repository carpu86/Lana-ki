from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend.memory.character_store import CharacterSheet
from backend.memory.qdrant_client import LanaMemory
from backend.services.intent_router import IntentRouter

logger = logging.getLogger(__name__)
router = APIRouter()

_intent_router = IntentRouter()
_memory = LanaMemory()


class ChatRequest(BaseModel):
    girl_id: str
    message: str
    temperature: float = 0.7
    user_id: str
    system_prompt_override: str | None = None


class ChatResponse(BaseModel):
    reply: str
    tokens_used: int
    provider: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> Any:
    character: CharacterSheet | None = await _memory.get_character(req.user_id, req.girl_id)

    if character is not None:
        system_prompt = (
            f"Du bist {character.name}, {character.age} Jahre alt.\n"
            f"Persönlichkeit: {character.personality}\n"
            f"Aussehen: {character.appearance}"
        )
    else:
        system_prompt = f"Du bist ein KI-Companion mit der ID '{req.girl_id}'."

    if req.system_prompt_override:
        system_prompt = req.system_prompt_override

    history = await _memory.get_recent(req.user_id, req.girl_id, n=20)
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    for entry in history:
        messages.append({"role": entry.role, "content": entry.content})
    messages.append({"role": "user", "content": req.message})

    result = await _intent_router.chat(
        messages=messages,
        temperature=req.temperature,
        max_tokens=512,
    )

    await _memory.store_message(req.user_id, req.girl_id, "user", req.message, {})
    await _memory.store_message(req.user_id, req.girl_id, "assistant", result.content, {
        "provider": result.provider,
        "tokens_used": result.tokens_used,
    })

    return ChatResponse(
        reply=result.content,
        tokens_used=result.tokens_used,
        provider=result.provider,
    )
