import requests
import json
import sys
import os
from dotenv import load_dotenv

# Lade die echten Umgebungsvariablen aus der .env
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(question):
    if not GEMINI_KEY:
        return "❌ FEHLER: GEMINI_API_KEY wurde in der .env nicht gefunden!"

    try:
        # KORREKTUR: Verwende das neueste verfügbare Modell gemini-2.5-flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"Du bist Lana, eine deutsche KI-Assistentin. Antworte kurz und präzise auf Deutsch:\n\n{question}"}]
            }]
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Gemini Fehler: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Gemini nicht erreichbar: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(ask_gemini(question))
    else:
        print("Verwendung: python lana_ki_fixed.py 'deine frage'")
