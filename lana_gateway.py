from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import os
import json
import time
import uuid
import requests

app = FastAPI(title="Lana RTX Gateway")

BASE_DIR   = Path("/home/carpu/lana-api")
STATIC_DIR = BASE_DIR / "static"
OUTPUT_DIR = BASE_DIR / "output"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DESKTOP_COMFY_URL = os.getenv("DESKTOP_COMFY_URL", "http://100.77.154.67:8188")

app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

class ChatPayload(BaseModel):
    character: str
    message: str
    history: list[str] = []
    message_count: int = 0

@app.get("/")
def root():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/api/health")
def health():
    comfy_reachable = False
    comfy_error = None
    try:
        r = requests.get(f"{DESKTOP_COMFY_URL}/system_stats", timeout=5)
        comfy_reachable = r.ok
        if not r.ok:
            comfy_error = f"HTTP {r.status_code}"
    except Exception as e:
        comfy_error = str(e)

    return {
        "ok": True,
        "desktop_comfy_url": DESKTOP_COMFY_URL,
        "comfy_reachable": comfy_reachable,
        "comfy_error": comfy_error
    }

@app.post("/api/chat")
def chat(payload: ChatPayload):
    reply = f"{payload.character}: Nachricht gespeichert -> {payload.message}"

    image_due = payload.message_count > 0 and payload.message_count % 5 == 0
    loop_due  = payload.message_count > 0 and payload.message_count % 15 == 0

    image_url = None
    loop_url  = None

    if image_due:
        fname = f"img_{uuid.uuid4().hex}.json"
        (OUTPUT_DIR / fname).write_text(json.dumps({
            "type": "image_job",
            "character": payload.character,
            "message": payload.message,
            "history": payload.history,
            "ts": time.time()
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        image_url = f"/output/{fname}"

    if loop_due:
        fname = f"loop_{uuid.uuid4().hex}.json"
        (OUTPUT_DIR / fname).write_text(json.dumps({
            "type": "loop_job",
            "character": payload.character,
            "message": payload.message,
            "history": payload.history,
            "ts": time.time()
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        loop_url = f"/output/{fname}"

    return {
        "reply": reply,
        "image_due": image_due,
        "loop_due": loop_due,
        "image_url": image_url,
        "loop_url": loop_url
    }
