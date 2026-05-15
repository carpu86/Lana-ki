from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid

import httpx

logger = logging.getLogger(__name__)

# Minimales ComfyUI-Workflow-Template (KSampler-basiert)
_WORKFLOW_TEMPLATE = {
    "3": {
        "inputs": {
            "seed": 0,
            "steps": 20,
            "cfg": 7,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0],
        },
        "class_type": "KSampler",
    },
    "4": {
        "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"},
        "class_type": "CheckpointLoaderSimple",
    },
    "5": {
        "inputs": {"width": 512, "height": 512, "batch_size": 1},
        "class_type": "EmptyLatentImage",
    },
    "6": {
        "inputs": {"text": "", "clip": ["4", 1]},
        "class_type": "CLIPTextEncode",
    },
    "7": {
        "inputs": {"text": "", "clip": ["4", 1]},
        "class_type": "CLIPTextEncode",
    },
    "8": {
        "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        "class_type": "VAEDecode",
    },
    "9": {
        "inputs": {
            "filename_prefix": "lana",
            "images": ["8", 0],
        },
        "class_type": "SaveImage",
    },
}


class ComfyUIClient:
    """Client für lokale ComfyUI-Instanz (RTX 4060, 8 GB VRAM)."""

    # VRAM-Limits
    MAX_WIDTH = 512
    MAX_HEIGHT = 512
    MAX_STEPS = 30

    def __init__(self) -> None:
        self.base_url = os.getenv("LANA_COMFYUI_BASE_URL", "http://127.0.0.1:8188")

    def _build_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
    ) -> dict:
        import copy
        import random

        w = min(width, self.MAX_WIDTH)
        h = min(height, self.MAX_HEIGHT)
        s = min(steps, self.MAX_STEPS)

        wf = copy.deepcopy(_WORKFLOW_TEMPLATE)
        wf["3"]["inputs"]["steps"] = s
        wf["3"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)
        wf["5"]["inputs"]["width"] = w
        wf["5"]["inputs"]["height"] = h
        wf["6"]["inputs"]["text"] = prompt
        wf["7"]["inputs"]["text"] = negative_prompt
        return wf

    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
    ) -> bytes:
        workflow = self._build_workflow(prompt, negative_prompt, width, height, steps)
        client_id = str(uuid.uuid4())

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow, "client_id": client_id},
            )
            resp.raise_for_status()
            prompt_id = resp.json()["prompt_id"]

            # Poll /history/{prompt_id} bis fertig
            for _ in range(120):
                await asyncio.sleep(1)
                hist = await client.get(f"{self.base_url}/history/{prompt_id}")
                hist.raise_for_status()
                data = hist.json()
                if prompt_id in data:
                    outputs = data[prompt_id].get("outputs", {})
                    for node_output in outputs.values():
                        images = node_output.get("images", [])
                        if images:
                            img_info = images[0]
                            img_resp = await client.get(
                                f"{self.base_url}/view",
                                params={
                                    "filename": img_info["filename"],
                                    "subfolder": img_info.get("subfolder", ""),
                                    "type": img_info.get("type", "output"),
                                },
                            )
                            img_resp.raise_for_status()
                            return img_resp.content

            raise TimeoutError("ComfyUI hat innerhalb von 120s kein Bild geliefert.")

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/system_stats")
                return resp.status_code == 200
        except Exception:
            return False
