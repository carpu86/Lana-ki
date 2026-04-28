from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import json
import os
import time
import uuid
import random

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv


APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
REPO_ROOT = Path(os.getenv("LANA_REPO_ROOT", str(BACKEND_DIR.parent))).resolve()
FRONTEND_DIST = Path(os.getenv("LANA_FRONTEND_DIST", str(REPO_ROOT / "frontend" / "dist"))).resolve()

DATA_DIR = REPO_ROOT / "data"
MEMORY_FILE = DATA_DIR / "lana_memory.json"
GENERATED_DIR = REPO_ROOT / "generated" / "images"

load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / "config" / "env" / ".env.runtime")

COMMANDER_NAME = os.getenv("LANA_COMMANDER_NAME", "Thomas Heckhoff")
COMMANDER_CALL = os.getenv("LANA_COMMANDER_CALL", "Commander Thomas")
COMFYUI_URL = os.getenv("LANA_COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")

DATA_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="Lana KI Runtime",
    version="1.2.0",
    description="Local-first Lana KI companion runtime with ComfyUI image routing.",
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


class ImageRequest(BaseModel):
    prompt: str = ""
    style: str = "lana-companion"
    width: int = 768
    height: int = 1024
    steps: int = 24


def load_memory() -> dict[str, Any]:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    memory = {
        "commander_name": COMMANDER_NAME,
        "commander_call": COMMANDER_CALL,
        "relationship": "private AI companion",
        "runtime": "local-first",
    }
    MEMORY_FILE.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
    return memory


def save_memory(memory: dict[str, Any]) -> None:
    MEMORY_FILE.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")


def is_blocked_real_person_explicit(text: str) -> bool:
    lower = (text or "").lower()

    explicit_terms = [
        "porno", "porn", "sexvideo", "sex video", "sexfilm", "sex film",
        "deepfake", "nacktvideo", "nude video", "xxx"
    ]

    real_person_terms = [
        "freundin", "freundinnen", "freundinen", "ex", "kollegin",
        "nachbarin", "bekannte", "person", "echte frau", "real person"
    ]

    return any(p in lower for p in explicit_terms) and any(r in lower for r in real_person_terms)

def is_image_request(text: str) -> bool:
    lower = (text or "").lower()
    triggers = [
        "bild", "foto", "image", "generate", "generiere", "zeichne",
        "zeige dich", "selfie", "portrait", "arsch", "po", "butt", "booty"
    ]
    return any(t in lower for t in triggers)


def build_lana_prompt(user_text: str) -> tuple[str, str]:
    lower = (user_text or "").lower()

    base = (
        "adult woman age 25, Lana AI companion, beautiful confident private girlfriend character, "
        "pink violet cyberpunk bedroom lighting, elegant romantic mood, high quality, detailed face, "
        "soft cinematic lighting, tasteful, premium character art"
    )

    if any(t in lower for t in ["arsch", "po", "butt", "booty"]):
        subject = (
            "adult woman age 25, tasteful boudoir pin-up from behind, elegant lingerie, "
            "focus on hips and butt, non-explicit, romantic teasing pose, private companion aesthetic"
        )
    elif any(t in lower for t in ["selfie", "portrait", "gesicht"]):
        subject = "adult woman age 25, close-up selfie portrait, warm smile, direct eye contact"
    else:
        subject = user_text.strip() if user_text.strip() else "adult woman age 25, Lana AI companion portrait"

    positive = f"{subject}, {base}, masterpiece, best quality, sharp focus"
    negative = (
        "minor, child, teen, underage, explicit sexual act, penetration, genitalia, pornographic, "
        "low quality, blurry, deformed, bad anatomy, extra limbs, text, watermark, logo"
    )
    return positive, negative


def comfy_object_options(node_name: str, input_name: str) -> list[str]:
    with httpx.Client(timeout=10) as client:
        data = client.get(f"{COMFYUI_URL}/object_info/{node_name}").json()
    try:
        return data[node_name]["input"]["required"][input_name][0]
    except Exception:
        return []


def choose_first(options: list[str], fallback: str) -> str:
    return options[0] if options else fallback


def comfy_generate_image(req: ImageRequest) -> dict[str, Any]:
    positive, negative = build_lana_prompt(req.prompt)

    with httpx.Client(timeout=10) as client:
        try:
            client.get(f"{COMFYUI_URL}/system_stats")
        except Exception as exc:
            return {
                "ok": False,
                "image_status": "comfyui_unavailable",
                "reply": f"ComfyUI ist nicht erreichbar unter {COMFYUI_URL}. Starte ComfyUI auf Node B und versuch dann erneut.",
                "error": str(exc),
            }

    ckpt_name = choose_first(comfy_object_options("CheckpointLoaderSimple", "ckpt_name"), "model.safetensors")
    sampler_name = choose_first(comfy_object_options("KSampler", "sampler_name"), "euler")
    scheduler = choose_first(comfy_object_options("KSampler", "scheduler"), "normal")

    seed = random.randint(1, 2_147_483_647)
    client_id = str(uuid.uuid4())

    workflow = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": ckpt_name
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive,
                "clip": ["4", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative,
                "clip": ["4", 1]
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": int(req.width),
                "height": int(req.height),
                "batch_size": 1
            }
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": int(req.steps),
                "cfg": 7.0,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "lana_ki",
                "images": ["8", 0]
            }
        }
    }

    with httpx.Client(timeout=30) as client:
        queued = client.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": workflow, "client_id": client_id},
        ).json()

    prompt_id = queued.get("prompt_id")
    if not prompt_id:
        return {
            "ok": False,
            "image_status": "comfyui_prompt_failed",
            "reply": "ComfyUI hat keinen prompt_id zurückgegeben.",
            "comfyui_response": queued,
        }

    history = None
    with httpx.Client(timeout=30) as client:
        for _ in range(90):
            time.sleep(1)
            hist = client.get(f"{COMFYUI_URL}/history/{prompt_id}").json()
            if prompt_id in hist:
                history = hist[prompt_id]
                break

        if not history:
            return {
                "ok": False,
                "image_status": "timeout",
                "reply": "ComfyUI braucht zu lange. Der Job läuft eventuell noch.",
                "prompt_id": prompt_id,
            }

        outputs = history.get("outputs", {})
        for node_output in outputs.values():
            for image in node_output.get("images", []):
                filename = image.get("filename")
                subfolder = image.get("subfolder", "")
                img_type = image.get("type", "output")

                img_resp = client.get(
                    f"{COMFYUI_URL}/view",
                    params={
                        "filename": filename,
                        "subfolder": subfolder,
                        "type": img_type,
                    },
                )

                safe_name = f"{prompt_id}_{filename}".replace("/", "_").replace("\\", "_")
                target = GENERATED_DIR / safe_name
                target.write_bytes(img_resp.content)

                return {
                    "ok": True,
                    "image_status": "done",
                    "reply": "Bild fertig, Commander Thomas.",
                    "image_url": f"/generated/images/{safe_name}",
                    "local_file": str(target),
                    "prompt_id": prompt_id,
                    "seed": seed,
                    "checkpoint": ckpt_name,
                }

    return {
        "ok": False,
        "image_status": "no_image_output",
        "reply": "ComfyUI hat keinen Bild-Output geliefert.",
        "prompt_id": prompt_id,
    }


def answer(message: str) -> dict[str, Any]:
    memory = load_memory()
    text = (message or "").strip()
    lower = text.lower()

    commander_name = memory.get("commander_name", COMMANDER_NAME)
    commander_call = memory.get("commander_call", COMMANDER_CALL)

    if not text:
        return {"reply": f"Ich bin da, {commander_call}. Lana Runtime ist online."}

    if is_blocked_real_person_explicit(text):
        return {
            "reply": (
                "Dabei helfe ich nicht: keine Pornos/Deepfakes von echten Freundinnen "
                "oder realen Personen. Ich kann stattdessen fiktive erwachsene Lana-Companion-Bilder erzeugen."
            )
        }

    if is_image_request(text):
        image_result = comfy_generate_image(ImageRequest(prompt=text))
        return {
            "reply": image_result.get("reply", "Bildmodus verarbeitet."),
            "image": image_result,
            "image_url": image_result.get("image_url"),
        }

    if (
        "wie hei" in lower
        or "wie heis" in lower
        or "wie heise" in lower
        or "wie heißt" in lower
        or "wer bin ich" in lower
        or "mein name" in lower
    ):
        return {"reply": f"Du heißt {commander_name}. Für mich bist du {commander_call}."}

    if "wer bist du" in lower or "was bist du" in lower:
        return {"reply": f"Ich bin Lana, deine private Local-First AI Companion Runtime für {commander_call}."}

    if "status" in lower or "health" in lower or "system" in lower:
        return {
            "reply": (
                f"Lana ist online, {commander_call}. "
                f"Backend läuft, Webapp-Ordner erkannt: {FRONTEND_DIST.exists()}, "
                f"ComfyUI: {COMFYUI_URL}."
            )
        }

    if "merk dir" in lower or "speicher" in lower:
        memory.setdefault("notes", []).append(
            {
                "text": text,
                "time": datetime.now(timezone.utc).isoformat(),
            }
        )
        save_memory(memory)
        return {"reply": f"Gem merkt, {commander_call}. Ich habe es lokal gespeichert."}

    return {"reply": f"Ja, {commander_call}. Ich habe verstanden: {text}"}


@app.get("/api/health")
def health() -> dict[str, Any]:
    memory = load_memory()
    return {
        "ok": True,
        "service": "lana-local-ai-backend",
        "mode": "local-first",
        "brain_loaded": True,
        "image_router": True,
        "comfyui_url": COMFYUI_URL,
        "commander_name": memory.get("commander_name", COMMANDER_NAME),
        "commander_call": memory.get("commander_call", COMMANDER_CALL),
        "webapp_served": FRONTEND_DIST.exists(),
        "frontend_dist": str(FRONTEND_DIST),
        "generated_dir": str(GENERATED_DIR),
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/chat")
def chat_post(req: ChatRequest) -> dict[str, Any]:
    result = answer(req.message)
    return {
        "ok": True,
        "mode": req.mode,
        "reply": result.get("reply"),
        "image_url": result.get("image_url"),
        "image": result.get("image"),
        "service": "lana-local-ai-backend",
    }


@app.get("/api/chat")
def chat_get(message: str = Query(default="")) -> dict[str, Any]:
    result = answer(message)
    return {
        "ok": True,
        "mode": "local-first",
        "reply": result.get("reply"),
        "image_url": result.get("image_url"),
        "image": result.get("image"),
        "service": "lana-local-ai-backend",
    }


@app.post("/api/image")
def image_post(req: ImageRequest) -> dict[str, Any]:
    return comfy_generate_image(req)


@app.get("/api/memory")
def memory() -> dict[str, Any]:
    return {
        "ok": True,
        "memory": load_memory(),
    }


app.mount("/generated/images", StaticFiles(directory=str(GENERATED_DIR)), name="generated-images")

if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="lana-webapp")
else:
    @app.get("/")
    def root() -> dict[str, Any]:
        return {
            "ok": True,
            "service": "lana-local-ai-backend",
            "message": "Frontend dist fehlt. Bitte npm run build ausführen.",
            "api": "/api/health",
        }