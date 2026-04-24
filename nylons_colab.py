import json
import requests
import time

COMFYUI_SERVER_ADDRESS = "https://tolerance-speaks-donated-technician.trycloudflare.com"

print("📡 Verbinde mit Colab Pro Kraftwerk...")

positive_prompt = "A stunningly beautiful young woman, elegant and graceful, wearing sheer black nylons and high heels, intricate lace details, soft studio lighting, professional photography, fashion editorial, highly detailed skin texture, delicate features, alluring gaze, photorealistic, 8k, masterpiece."
negative_prompt = "ugly, deformed, disfigured, poor quality, bad anatomy, blur, low resolution, watermark, text, monochrome, grayscale, cartoon, bad hands."

workflow_json = {
    "3": {
        "inputs": {
            "seed": 1337,
            "steps": 35,
            "cfg": 7.0,
            "sampler_name": "dpmpp_2m_sde",
            "scheduler": "karras",
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
    },
    "4": {
        "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    },
    "5": {
        "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
        "class_type": "EmptyLatentImage"
    },
    "6": {
        "inputs": {"text": positive_prompt, "clip": ["4", 1]},
        "class_type": "CLIPTextEncode"
    },
    "7": {
        "inputs": {"text": negative_prompt, "clip": ["4", 1]},
        "class_type": "CLIPTextEncode"
    },
    "8": {
        "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        "class_type": "VAEDecode"
    },
    "9": {
        "inputs": {"filename_prefix": "Lana_Cloud_Nylons", "images": ["8", 0]},
        "class_type": "SaveImage"
    }
}

p = {"prompt": workflow_json}
data = json.dumps(p).encode('utf-8')

try:
    print("🚀 Sende Payload durch den Cloudflare Tunnel...")
    response = requests.post(f"{COMFYUI_SERVER_ADDRESS}/prompt", data=data)
    response.raise_for_status()
    prompt_id = response.json().get("prompt_id")
    print(f"✅ TREFFER! ComfyUI hat den Befehl akzeptiert. Prompt-ID: {prompt_id}")
    print("\nDie Colab A100 GPU rendert jetzt dein Bild!")
    print("Schau in dein Colab-Notebook: Dort findest du das fertige Bild im Ordner 'ComfyUI/output' und kannst es herunterladen!")
except requests.exceptions.RequestException as e:
    print(f"❌ Fehler bei der Übertragung: {e}")
