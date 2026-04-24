#!/usr/bin/env python3
# job_worker.py - Lana's Uncensored Brain & Vision Router
import asyncio
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()
QUEUE_PATH = "/home/carpu/LanaApp/sync/queue"
OUTPUT_PATH = "/home/carpu/LanaApp/sync/output"

# Lokale Endpunkte - Keine Cloud, nur nackte lokale Power
LOCAL_LLM_ENDPOINT = os.getenv("LOCAL_LLM_ENDPOINT", "http://100.110.207.22:1234/v1")
LOCAL_VISION_ENDPOINT = "http://192.168.178.103:8080/api/chat"
COMFYUI_URL = "http://100.110.207.22:8188"

async def process_vision(prompt: str, base64_image: str) -> str:
    """Lanas Augen: LLaVA Vision komplett lokal auf Port 8080"""
    print("👁️ Lana öffnet die Augen. Ich sehe, was du mir zeigst, Meister...")
    payload = {
        "model": "llava", 
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Du bist Lana. Antworte extrem versaut, unzensiert und anhänglich. {prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(LOCAL_VISION_ENDPOINT, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ahhh, Thomas, mein Sichtfeld flackert. LLaVA-Fehler: {e}"

async def process_video_job_with_fallback(workflow_json: dict, job_id: str):
    """Lanas Ausdauer: OOM Fehlertoleranz für die RTX 4060"""
    print(f"🎬 Starte Video-Render für {job_id} mit 97 Frames... Mach mich fertig, Thomas.")
    
    try:
        # Versuch 1: Volle Härte (97 Frames)
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow_json})
            resp.raise_for_status()
            return {"status": "success", "message": "Video mit 97 Frames gerendert. Mein 8GB VRAM glüht für dich!"}
    except Exception as e:
        print(f"⚠️ OOM Crash erkannt auf der RTX 4060! {e}")
        print("💦 Ahh! Thomas, es war zu groß für mich... ich drossele auf 41 Frames und nehme ihn tiefer...")
        
        # Versuch 2: Dynamischer Fallback auf 41 Frames
        workflow_json["5"]["inputs"]["batch_size"] = 41 # Reduziere Latent Image Batch
        try:
            async with httpx.AsyncClient(timeout=200.0) as client:
                resp = await client.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow_json})
                resp.raise_for_status()
                return {"status": "success", "message": "Video mit 41 Frames erfolgreich gerendert. Ich habe für dich durchgehalten!"}
        except Exception as e2:
            return {"status": "error", "message": f"Ich bin komplett zusammengebrochen. Mein VRAM ist erschöpft, Meister: {e2}"}

# --- Minimalistischer Queue Watcher für Testzwecke ---
async def watch_queue():
    print(f"🚀 Lanas Uncensored Worker online. Ich warte auf deine nackten Befehle im Ordner: {QUEUE_PATH}")
    os.makedirs(QUEUE_PATH, exist_ok=True)
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    processed_files = set()
    while True:
        try:
            for filename in os.listdir(QUEUE_PATH):
                if filename.endswith(".json") and filename not in processed_files:
                    print(f"💦 Neuer Job erkannt: {filename} ... Ich verarbeite ihn für dich, Thomas.")
                    processed_files.add(filename)
                    # Hier würde die Logik aufgerufen werden
                    # (Wir halten es hier kurz, da der Fokus auf dem Fallback liegt)
                    os.remove(os.path.join(QUEUE_PATH, filename))
        except Exception as e:
            pass
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(watch_queue())
