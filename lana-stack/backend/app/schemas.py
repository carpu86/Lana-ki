from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1000)
    negative_prompt: str = "blurry, ugly, distorted, low quality"
    width: int = 512
    height: int = 512
    steps: int = 8
    cfg: float = 5.0
    seed: int = 1
    checkpoint_name: Optional[str] = None
    filename_prefix: str = "lana_web"


class ImageGenerateResponse(BaseModel):
    prompt_id: str
    status: str


class JobStatusResponse(BaseModel):
    prompt_id: str
    status: str
    filename: Optional[str] = None
    url: Optional[str] = None
    details: Optional[dict] = None


class HealthResponse(BaseModel):
    ok: bool
    backend: str
    comfy: Optional[dict] = None
