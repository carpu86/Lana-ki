from __future__ import annotations

import copy
import logging
from typing import Any

import httpx

from backend.config import Settings

LOGGER = logging.getLogger(__name__)


class ComfyUIClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def sanitize_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        sanitized = copy.deepcopy(workflow)
        sanitized["lowvram"] = True
        sanitized.setdefault("lana_constraints", {})
        sanitized["lana_constraints"].update(
            {
                "lowvram": True,
                "max_resolution": [512, 512],
                "vae_decode": "TiledVAEDecode",
            }
        )
        return self._sanitize_node(sanitized)

    def _sanitize_node(self, value: Any) -> Any:
        if isinstance(value, dict):
            sanitized: dict[str, Any] = {}
            for key, item in value.items():
                if key in {"width", "height", "max_width", "max_height"} and isinstance(item, int):
                    sanitized[key] = min(item, 512)
                elif key == "lowvram":
                    sanitized[key] = True
                elif key == "class_type" and item == "VAEDecode":
                    sanitized[key] = "TiledVAEDecode"
                else:
                    sanitized[key] = self._sanitize_node(item)
            return sanitized
        if isinstance(value, list):
            return [self._sanitize_node(item) for item in value]
        return value

    async def run_workflow(self, workflow: dict[str, Any], client_id: str = "lana") -> dict[str, Any]:
        sanitized = self.sanitize_workflow(workflow)
        payload = {"prompt": sanitized, "client_id": client_id}
        async with httpx.AsyncClient(timeout=self.settings.lana_timeout_seconds) as client:
            response = await client.post(f"{self.settings.lana_comfyui_url}/prompt", json=payload)
            response.raise_for_status()
            body = response.json()
        LOGGER.info("ComfyUI-Workflow eingereicht: %s", body)
        return {"provider": "comfyui", "workflow": sanitized, "result": body}
