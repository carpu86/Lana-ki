from __future__ import annotations

import base64
import logging
import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.comfyui_client import ComfyUIClient

logger = logging.getLogger(__name__)
router = APIRouter()

_comfyui = ComfyUIClient()

_RUNPOD_URL = os.getenv("NODE_A_RUNPOD_ENDPOINT_URL") or os.getenv(
    "NODE_B_RUNPOD_ENDPOINT_URL"
)


class ImageRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = Field(default=512, ge=64, le=512)
    height: int = Field(default=512, ge=64, le=512)
    steps: int = Field(default=20, ge=1, le=30)
    girl_id: str | None = None


class ImageResponse(BaseModel):
    url: str
    provider: str
    metadata: dict


@router.post("/image", response_model=ImageResponse)
async def generate_image(req: ImageRequest) -> Any:
    comfy_ok = await _comfyui.health_check()

    if comfy_ok:
        try:
            image_bytes = await _comfyui.generate(
                prompt=req.prompt,
                negative_prompt=req.negative_prompt,
                width=req.width,
                height=req.height,
                steps=req.steps,
            )
            b64 = base64.b64encode(image_bytes).decode()
            return ImageResponse(
                url=f"data:image/png;base64,{b64}",
                provider="comfyui",
                metadata={
                    "width": req.width,
                    "height": req.height,
                    "steps": req.steps,
                },
            )
        except Exception as exc:
            logger.warning("ComfyUI failed, trying RunPod fallback: %s", exc)

    if _RUNPOD_URL:
        try:
            payload = {
                "input": {
                    "prompt": req.prompt,
                    "negative_prompt": req.negative_prompt,
                    "width": req.width,
                    "height": req.height,
                    "num_inference_steps": req.steps,
                }
            }
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(_RUNPOD_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
                image_url = data.get("output", {}).get("url", "")
                return ImageResponse(
                    url=image_url,
                    provider="runpod",
                    metadata={
                        "width": req.width,
                        "height": req.height,
                        "steps": req.steps,
                    },
                )
        except Exception as exc:
            logger.error("RunPod fallback failed: %s", exc)

    raise HTTPException(status_code=503, detail="Alle Bild-Provider nicht erreichbar.")
