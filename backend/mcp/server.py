from __future__ import annotations

import hmac
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from json import JSONDecodeError
from fastapi.responses import JSONResponse
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



    def mcp_json_response(payload: dict[str, Any], status_code: int = status.HTTP_200_OK) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )

    def mcp_error_response(request_id: Any, code: int, message: str, status_code: int) -> JSONResponse:
        return mcp_json_response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": code, "message": message},
            },
            status_code=status_code,
        )

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
        summary="Führt ein Lana MCP Tool aus",
        description="Streamable-HTTP-kompatibler Einstiegspunkt für registrierte Lana-MCP-Tools.",
    )
    async def invoke_tool(request: Request) -> JSONResponse:
        settings, registry = validate_token(request)
        try:
            payload = await request.json()
        except JSONDecodeError:
            return mcp_error_response(None, -32700, "Ungültiges JSON im Request-Body", status.HTTP_400_BAD_REQUEST)

        if isinstance(payload, dict) and payload.get("method"):
            request_id = payload.get("id")
            method = payload.get("method")

            if method == "initialize":
                return mcp_json_response(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "serverInfo": {"name": "lana_ki_mcp", "version": "1.0.0"},
                            "capabilities": {"tools": {}},
                        },
                    }
                )

            if method == "tools/list":
                tools = sorted(registry.tools.keys())
                return mcp_json_response(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": [
                                {"name": name, "description": f"Lana MCP tool: {name}", "inputSchema": {"type": "object"}}
                                for name in tools
                            ]
                        },
                    }
                )

            if method == "tools/call":
                params = payload.get("params") or {}
                tool_name = params.get("name")
                arguments = params.get("arguments") or {}
                if not tool_name:
                    return mcp_error_response(request_id, -32602, "tools/call benötigt params.name", status.HTTP_400_BAD_REQUEST)
                try:
                    result = await registry.invoke(tool_name, arguments)
                except KeyError as exc:
                    return mcp_error_response(request_id, -32601, str(exc), status.HTTP_404_NOT_FOUND)
                except Exception as exc:
                    message = str(exc)
                    status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "Kontext nicht verfügbar" in message else status.HTTP_400_BAD_REQUEST
                    return mcp_error_response(request_id, -32000, message, status_code)

                return mcp_json_response(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"content": [{"type": "text", "text": str(result)}]},
                    }
                )

            return mcp_error_response(request_id, -32601, f"Methode nicht unterstützt: {method}", status.HTTP_400_BAD_REQUEST)

        try:
            tool_payload = MCPToolRequest.model_validate(payload)
            result = await registry.invoke(tool_payload.tool, tool_payload.arguments)
        except KeyError as exc:
            return mcp_json_response({"ok": False, "error": str(exc)}, status_code=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            message = str(exc)
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "Kontext nicht verfügbar" in message else status.HTTP_400_BAD_REQUEST
            return mcp_json_response({"ok": False, "error": message}, status_code=status_code)

        return mcp_json_response(
            MCPToolResponse(
                ok=True,
                transport=settings.lana_mcp_transport,
                endpoint=settings.lana_mcp_public_endpoint,
                tool=tool_payload.tool,
                result=result,
            ).model_dump()
        )

    return router
