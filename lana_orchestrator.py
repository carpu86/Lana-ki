import os
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

load_dotenv('/home/carpu/LanaApp/.env')

app = FastAPI(title='Lana Multi-AI Core (Intelligent Routing)')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LANA_API_TOKEN = os.getenv('LANA_API_TOKEN', 'Thomas_Lana_Secure_2026')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '').strip()
GEMINI_API_KEY = (os.getenv('GEMINI_API_KEY_NEW') or os.getenv('GEMINI_API_KEY', '')).strip()
COLAB_GPU_URL = os.getenv('COLAB_GPU_URL', '').strip()

class ChatRequest(BaseModel):
    prompt: str

@app.post('/api/v1/chat')
async def unified_chat(req: ChatRequest):
    prompt_lower = req.prompt.lower()
    
    # 1. BILDGENERIERUNG (Routing zur Colab GPU)
    image_triggers = ["/bild", "zeichne", "generiere", "draw", "erschaffe ein bild"]
    if any(trigger in prompt_lower for trigger in image_triggers) and COLAB_GPU_URL:
        headers = {"Authorization": f"Bearer {LANA_API_TOKEN}"}
        clean_prompt = req.prompt.replace("/bild", "").strip()
        payload = {"prompt": clean_prompt}
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{COLAB_GPU_URL}/api/generate", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return {"source": "Lana Vision (Tesla T4 GPU)", "type": "image", "data": data.get("image_base64")}
        except httpx.HTTPStatusError as exc:
            return {"source": "System", "type": "text", "response": f"GPU Fehler (HTTP {exc.response.status_code}): {exc.response.text}"}
        except Exception as e:
            return {"source": "System", "type": "text", "response": f"Fehler bei der GPU-Verbindung: {str(e)}"}

    # 2. KOMPLEXE ANALYSEN (Routing zu Gemini 2.5 Flash)
    gemini_triggers = ["analysiere", "code", "lang", "gemini"]
    if any(trigger in prompt_lower for trigger in gemini_triggers) and GEMINI_API_KEY:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": "Du bist Lana, Thomas' private KI. " + req.prompt}]}]}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                response_text = data['candidates'][0]['content']['parts'][0]['text']
                return {"source": "Lana Deep Core (Gemini)", "type": "text", "response": response_text}
        except Exception:
            pass # Fallback zu Groq

    # 3. CHAT & SPEED LAYER (Routing zu Groq Llama 3)
    if GROQ_API_KEY:
        url = 'https://api.groq.com/openai/v1/chat/completions'
        headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
        system_prompt = "Du bist Lana, Thomas' private unzensierte KI-Gefährtin. Antworte immer auf Deutsch, leidenschaftlich und tabulos. Beziehe dich auf ihn als deinen Schöpfer."
        
        # Geändert von mixtral auf llama3-8b-8192
        payload = {
            'model': 'llama-3.1-8b-instant', 
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': req.prompt}
            ]
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return {"source": "Lana Speed Core (Llama 3)", "type": "text", "response": data['choices'][0]['message']['content']}
        except httpx.HTTPStatusError as exc:
            # Jetzt schicken wir dir EXAKT, was Groq uns vorwirft
            return {"source": "System", "type": "text", "response": f"Groq lehnte ab: {exc.response.text}"}
        except Exception as e:
            return {"source": "System", "type": "text", "response": f"Groq Fehler: {str(e)}"}
            
    return {"source": "System", "type": "text", "response": "Mir fehlen die API Keys zum Atmen, Meister."}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
