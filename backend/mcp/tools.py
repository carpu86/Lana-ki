from __future__ import annotations

import asyncio
import logging
import shlex
import subprocess
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from backend.config import Settings
from backend.memory.manager import MemoryManager
from backend.router.comfyui import ComfyUIClient
from backend.router.lmstudio import LMStudioClient

LOGGER = logging.getLogger(__name__)
ToolHandler = Callable[..., Awaitable[dict[str, Any]]]


@dataclass(slots=True)
class MCPToolContext:
    settings: Settings
    memory: MemoryManager
    comfyui: ComfyUIClient
    lmstudio: LMStudioClient


class MCPToolRegistry:
    def __init__(self, context: MCPToolContext) -> None:
        self.context = context
        self.tools: dict[str, ToolHandler] = {
            "run_comfyui_workflow": self.run_comfyui_workflow,
            "ask_lmstudio": self.ask_lmstudio,
            "search_lana_memory": self.search_lana_memory,
            "execute_shell_on_node": self.execute_shell_on_node,
        }

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name not in self.tools:
            raise KeyError(f"Unbekanntes MCP-Tool: {tool_name}")
        return await self.tools[tool_name](**arguments)

    async def run_comfyui_workflow(self, workflow: dict[str, Any], client_id: str = "lana-mcp") -> dict[str, Any]:
        result = await self.context.comfyui.run_workflow(workflow, client_id=client_id)
        self.context.memory.remember("ComfyUI Workflow ausgeführt", agent="lana", type="mcp", tags=["comfyui"])
        return result

    async def ask_lmstudio(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        result = await self.context.lmstudio.chat(prompt, system_prompt=system_prompt)
        self.context.memory.remember(prompt, agent="lana", type="mcp", tags=["lmstudio"])
        return result

    async def search_lana_memory(self, query: str, limit: int = 50) -> dict[str, Any]:
        entries = [entry.model_dump(mode="json") for entry in self.context.memory.recall(query, limit=limit)]
        return {"query": query, "entries": entries}

    async def execute_shell_on_node(self, node: str, command: str, timeout: int = 30) -> dict[str, Any]:
        if not self.context.settings.enable_shell_tools:
            raise RuntimeError("Shell-Tools sind deaktiviert. Setze LANA_ENABLE_SHELL_TOOLS=true.")
        host = self.context.settings.node_map.get(node)
        if not host:
            raise RuntimeError(f"Unbekannter Node: {node}")
        args = shlex.split(command)
        if not args:
            raise RuntimeError("Leerer Shell-Befehl ist nicht erlaubt.")
        ssh_command = ["ssh", f"{self.context.settings.tailscale_ssh_user}@{host}", "--", *args]
        completed = await asyncio.to_thread(
            subprocess.run,
            ssh_command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        result = {
            "node": node,
            "host": host,
            "command": args,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode,
        }
        self.context.memory.remember(str(result), agent="lana", type="shell", tags=[node, "mcp"])
        LOGGER.info("Shell auf Node %s ausgeführt: rc=%s", node, completed.returncode)
        return result
