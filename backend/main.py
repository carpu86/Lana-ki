from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

from backend.agents.scheduler import AutonomousScheduler
from backend.config import configure_logging, get_settings, validate_required_settings
from backend.mcp.server import create_mcp_router
from backend.mcp.tools import MCPToolContext, MCPToolRegistry
from backend.memory.manager import MemoryManager
from backend.router.agent_router import AgentRouter, ChatRouteResult
from backend.router.comfyui import ComfyUIClient
from backend.router.lmstudio import LMStudioClient


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User-Prompt für Lana")
    system_prompt: str | None = Field(default=None, description="Optionaler System-Prompt")
    session_id: str | None = Field(default=None, description="Optionale Session-ID")
    tags: list[str] = Field(default_factory=list, description="Zusätzliche Memory-Tags")


@dataclass(slots=True)
class AppContext:
    settings: Any
    memory: MemoryManager
    agent_router: AgentRouter
    comfyui: ComfyUIClient
    lmstudio: LMStudioClient
    mcp_registry: MCPToolRegistry
    scheduler: AutonomousScheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    validate_required_settings(settings)
    memory = MemoryManager(settings)
    agent_router = AgentRouter(settings)
    comfyui = ComfyUIClient(settings)
    lmstudio = LMStudioClient(settings)
    mcp_registry = MCPToolRegistry(MCPToolContext(settings=settings, memory=memory, comfyui=comfyui, lmstudio=lmstudio))
    scheduler = AutonomousScheduler(memory, mcp_registry, interval_seconds=settings.scheduler_interval_seconds)
    scheduler.start()
    app.state.context = AppContext(
        settings=settings,
        memory=memory,
        agent_router=agent_router,
        comfyui=comfyui,
        lmstudio=lmstudio,
        mcp_registry=mcp_registry,
        scheduler=scheduler,
    )
    try:
        yield
    finally:
        scheduler.stop()


app = FastAPI(
    title="Lana KI Orchestrator",
    version="1.0.0",
    description="FastAPI Orchestrator für Lana KI mit Routing, Memory, MCP und autonomen Agentinnen.",
    lifespan=lifespan,
)
app.include_router(create_mcp_router())


def get_context(request: Request) -> AppContext:
    return request.app.state.context


@app.get(
    "/",
    summary="Lana Root Endpoint",
    description="Liefert einen kompakten Status des Lana KI Orchestrators.",
)
async def root() -> dict[str, Any]:
    return {"ok": True, "service": "lana-ki-orchestrator", "docs": "/docs"}


@app.get(
    "/health",
    summary="Health-Check",
    description="Prüft, ob der Orchestrator gestartet ist und Kernkomponenten initialisiert wurden.",
)
@app.get("/api/health", include_in_schema=False)
async def health(request: Request) -> dict[str, Any]:
    context = get_context(request)
    return {
        "ok": True,
        "service": context.settings.service_name,
        "version": context.settings.service_version,
        "node": context.settings.lana_node_name,
        "time": datetime.now(timezone.utc).isoformat(),
        "scheduler_running": context.scheduler.status()["running"],
        "memory_db": str(context.memory.db_path),
    }


@app.get(
    "/status",
    summary="Detailstatus des Orchestrators",
    description="Zeigt Routing-Endpunkte, Ports, Memory-Pfade und Scheduler-Status.",
)
@app.get("/api/system", include_in_schema=False)
async def status(request: Request) -> dict[str, Any]:
    context = get_context(request)
    return {
        "ok": True,
        "routing": {
            "lmstudio": context.settings.lana_lmstudio_url,
            "gemini_model": context.settings.lana_gemini_model,
            "openai_base_url": context.settings.openai_base_url,
            "timeout_seconds": context.settings.lana_timeout_seconds,
        },
        "ports": {
            "telegram": context.settings.telegram_bot_port,
            "orchestrator": context.settings.lana_api_port,
            "vision": context.settings.lana_vision_port,
            "comfyui": 8188,
            "lmstudio": 1234,
        },
        "paths": {
            "log_root": context.settings.lana_log_root,
            "backup_root": context.settings.lana_backup_root,
            "runtime_root": context.settings.lana_runtime_root,
            "audit_root": context.settings.lana_audit_root,
            "sync_folder": context.settings.sync_folder_path,
        },
        "mcp": {
            "transport": context.settings.lana_mcp_transport,
            "endpoint": context.settings.lana_mcp_public_endpoint,
            "tools": sorted(context.mcp_registry.tools.keys()),
        },
        "scheduler": context.scheduler.status(),
    }


@app.post(
    "/v1/chat",
    summary="Lana Chat Endpoint",
    description="Routet Chat-Anfragen lokal zu LM Studio, dann zu Gemini und zuletzt zu OpenAI.",
)
@app.post("/api/chat", include_in_schema=False)
async def chat(payload: ChatRequest, request: Request) -> dict[str, Any]:
    context = get_context(request)
    route_result: ChatRouteResult = await context.agent_router.route_chat(
        payload.prompt,
        system_prompt=payload.system_prompt,
    )
    memory_tags = ["chat", route_result.provider, *payload.tags]
    context.memory.remember(
        payload.prompt,
        agent="user",
        type="chat_prompt",
        tags=memory_tags,
        session_id=payload.session_id,
    )
    context.memory.remember(
        route_result.reply,
        agent="lana",
        type="chat_reply",
        tags=memory_tags,
        session_id=payload.session_id,
    )
    context.scheduler.publish_event(f"Chat über {route_result.provider}: {payload.prompt[:120]}")
    return {"ok": True, **route_result.model_dump(mode="json")}
