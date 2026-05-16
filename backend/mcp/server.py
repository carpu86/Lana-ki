from __future__ import annotations

import hmac
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field


class MCPToolRequest(BaseModel):
    tool: str = Field(..., description="Registrierter MCP-Tool-Name")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Tool-Argumente")


class MCPToolResponse(BaseModel):
    ok: bool
    transport: str
    endpoint: str
    tool: str
    result: dict[str, Any]


def create_mcp_router() -> APIRouter:
    router = APIRouter(tags=["mcp"])

    def get_runtime(request: Request) -> tuple[Any, Any]:
        context = request.app.state.context
        return context.settings, context.mcp_registry

    def validate_token(request: Request) -> tuple[Any, Any]:
        settings, registry = get_runtime(request)
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer-Token fehlt.")
        token = header.removeprefix("Bearer ").strip()
        expected = settings.resolved_mcp_bearer_token()
        if not expected:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MCP-Token nicht konfiguriert.")
        if not hmac.compare_digest(token, expected):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ungültiger MCP-Token.")
        return settings, registry

    @router.get(
        "/mcp",
        summary="Beschreibt den Lana MCP Server",
        description="Liefert Transport, öffentliches Gateway und registrierte Tools des Lana MCP Servers.",
    )
    async def describe(request: Request) -> dict[str, Any]:
        settings, registry = validate_token(request)
        return {
            "transport": settings.lana_mcp_transport,
            "endpoint": settings.lana_mcp_public_endpoint,
            "tools": sorted(registry.tools.keys()),
        }

    @router.post(
        "/mcp",
        response_model=MCPToolResponse,
        summary="Führt ein Lana MCP Tool aus",
        description="Streamable-HTTP-kompatibler Einstiegspunkt für registrierte Lana-MCP-Tools.",
    )
    async def invoke_tool(request: Request, payload: MCPToolRequest) -> MCPToolResponse:
        settings, registry = validate_token(request)
        try:
            result = await registry.invoke(payload.tool, payload.arguments)
        except KeyError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return MCPToolResponse(
            ok=True,
            transport=settings.lana_mcp_transport,
            endpoint=settings.lana_mcp_public_endpoint,
            tool=payload.tool,
            result=result,
        )

    return router
