import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.routers import chat, image, mcp  # noqa: E402  (after load_dotenv)

LMSTUDIO_BASE_URL = os.getenv("LANA_LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
COMFYUI_BASE_URL = os.getenv("LANA_COMFYUI_BASE_URL", "http://127.0.0.1:8188")

_CORS_ORIGINS_RAW = os.getenv(
    "LANA_CORS_ORIGINS",
    "https://lana-ki.de,https://gateway.lana-ki.de",
)
CORS_ORIGINS = [o.strip() for o in _CORS_ORIGINS_RAW.split(",") if o.strip()]


async def _check_lm_studio() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{LMSTUDIO_BASE_URL}/models")
            return resp.status_code == 200
    except Exception:
        return False


async def _check_comfyui() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{COMFYUI_BASE_URL}/system_stats")
            return resp.status_code == 200
    except Exception:
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    lm_ok = await _check_lm_studio()
    comfy_ok = await _check_comfyui()
    print(
        f"[startup] LM Studio: {'✓' if lm_ok else '✗'}  "
        f"ComfyUI: {'✓' if comfy_ok else '✗'}"
    )
    from backend.scheduler import start_scheduler
    start_scheduler()
    yield


app = FastAPI(
    title="Lana KI Orchestrator API",
    version="1.0.0",
    description="Lana KI Master-Orchestrator — deployed auf 192.168.178.101:8024",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(image.router)
app.include_router(mcp.router)


@app.get("/health")
async def health() -> dict[str, Any]:
    lm_ok, comfy_ok = await asyncio.gather(_check_lm_studio(), _check_comfyui())

    azure_key = bool(os.getenv("AZURE_OPENAI_API_KEY"))
    gemini_key = bool(os.getenv("GEMINI_API_KEY"))
    runpod_url = bool(
        os.getenv("NODE_A_RUNPOD_ENDPOINT_URL") or os.getenv("NODE_B_RUNPOD_ENDPOINT_URL")
    )

    return {
        "ok": True,
        "time": datetime.now(timezone.utc).isoformat(),
        "p0": {
            "lm_studio": lm_ok,
            "comfyui": comfy_ok,
        },
        "p1": {
            "azure": azure_key,
            "gemini": gemini_key,
        },
        "p2": {
            "runpod": runpod_url,
        },
    }
