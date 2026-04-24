# === LANA-KI COLAB PRO SETUP ===
# Diesen Code in dein Colab Pro Notebook kopieren

# 1. Pakete installieren
!pip install -q google-cloud-storage google-auth google-auth-oauthlib
!pip install -q fastapi uvicorn aiohttp aiofiles pyngrok
!pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 2. Imports
from google.colab import auth
from google.cloud import storage
from pyngrok import ngrok
import os, json, threading
from datetime import datetime
from fastapi import FastAPI
import uvicorn
import torch

# 3. Google Cloud Authentication
auth.authenticate_user()
project_id = "lana-ki-unified-2026"
os.environ['GOOGLE_CLOUD_PROJECT'] = project_id

# 4. Storage Client
client = storage.Client(project=project_id)

# 5. GPU Check
print(f"🎮 CUDA verfügbar: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"🎮 CUDA Version: {torch.version.cuda}")

# 6. FastAPI Server
app = FastAPI(title="Lana-KI Colab API")

@app.get("/")
def root():
    return {
        "status": "Lana-KI Colab API aktiv", 
        "gpu": torch.cuda.is_available(),
        "project": project_id
    }

@app.get("/gpu-status")
def gpu_status():
    return {
        "cuda_available": torch.cuda.is_available(),
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None
    }

@app.post("/execute")
def execute_code(code: dict):
    try:
        exec_globals = {}
        exec(code.get("code", ""), exec_globals)
        return {"success": True, "result": "Code ausgeführt"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 7. Server starten
def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# 8. Ngrok Tunnel
public_url = ngrok.connect(8000)
print(f"🌐 Public URL: {public_url}")

# 9. Tunnel Info speichern
tunnel_info = {
    "public_url": str(public_url),
    "timestamp": datetime.now().isoformat(),
    "gpu_available": torch.cuda.is_available(),
    "project_id": project_id
}

bucket_name = f"lana-ki-outputs-lana-ki-unified-2026"
try:
    bucket = client.bucket(bucket_name)
    blob = bucket.blob('tunnel_info.json')
    blob.upload_from_string(json.dumps(tunnel_info, indent=2))
    print(f"✅ Tunnel Info gespeichert")
except Exception as e:
    print(f"⚠️ Upload Fehler: {e}")

print("🚀 LANA-KI COLAB PRO SETUP ABGESCHLOSSEN!")
print(f"📡 Tunnel URL: {public_url}")
