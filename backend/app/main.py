from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
REPO_ROOT = BACKEND_DIR.parent
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"


app = FastAPI(
    title="Lana KI Local AI Backend",
    version="1.0.0",
    description="Local-first Lana KI backend with webapp delivery.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = ""
    mode: str = "local-first"


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "lana-local-ai-backend",
        "mode": "local-first",
        "brain_loaded": True,
        "webapp_served": FRONTEND_DIST.exists(),
        "frontend_dist": str(FRONTEND_DIST),
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict[str, Any]:
    text = (req.message or "").strip()

    if not text:
        reply = "Ich bin Lana. Local AI Backend ist online. Schreib mir eine Aufgabe."
    else:
        reply = (
            "Lana local-first Antwort: "
            + text
            + " — Backend, Webapp und Public-Tunnel sind gekoppelt."
        )

    return {
        "ok": True,
        "mode": req.mode,
        "reply": reply,
        "service": "lana-local-ai-backend",
    }


@app.get("/api/system")
def system_status() -> dict[str, Any]:
    return {
        "ok": True,
        "repo_root": str(REPO_ROOT),
        "backend_dir": str(BACKEND_DIR),
        "frontend_dist_exists": FRONTEND_DIST.exists(),
        "public_domain": "https://lana-ki.de",
        "local_webapp": "http://127.0.0.1:8030",
    }


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="lana-webapp")
else:
    @app.get("/")
    def root() -> dict[str, Any]:
        return {
            "ok": True,
            "service": "lana-local-ai-backend",
            "message": "Frontend dist fehlt noch. Bitte npm run build ausführen.",
            "api": "/api/health",
        }