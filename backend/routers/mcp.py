from __future__ import annotations

import logging
from typing import Any, AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.agents.companion_agent import CompanionAgent
from backend.memory.qdrant_client import LanaMemory
from backend.services.intent_router import IntentRouter

logger = logging.getLogger(__name__)
router = APIRouter()

_intent_router = IntentRouter()
_memory = LanaMemory()


class MCPRequest(BaseModel):
    agent: str
    user_id: str
    girl_id: str | None = None
    action: str
    payload: dict[str, Any] = {}


@router.post("/mcp")
async def mcp_endpoint(req: MCPRequest) -> StreamingResponse:
    return StreamingResponse(
        _dispatch(req),
        media_type="text/event-stream",
    )


async def _dispatch(req: MCPRequest) -> AsyncGenerator[str, None]:
    try:
        if req.agent == "companion" and req.girl_id:
            character = await _memory.get_character(req.user_id, req.girl_id)
            agent = CompanionAgent(
                user_id=req.user_id,
                girl_id=req.girl_id,
                character_sheet=character,
            )
            if req.action == "respond":
                user_message = req.payload.get("message", "")
                reply = await agent.respond_to_user(user_message)
                yield f"data: {reply}\n\n"
            elif req.action == "proactive":
                reply = await agent.generate_proactive_message()
                yield f"data: {reply}\n\n"
            elif req.action == "mood":
                mood = await agent.update_mood(req.payload)
                yield f"data: {mood.value}\n\n"
            else:
                yield "data: [error] Unbekannte Action.\n\n"
        elif req.agent == "intent":
            messages = req.payload.get("messages", [])
            temperature = float(req.payload.get("temperature", 0.7))
            result = await _intent_router.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=512,
            )
            yield f"data: {result.content}\n\n"
        else:
            yield "data: [error] Unbekannter Agent.\n\n"
    except Exception as exc:
        logger.error("MCP dispatch error: %s", exc)
        yield "data: [error] Interner Fehler. Bitte erneut versuchen.\n\n"
