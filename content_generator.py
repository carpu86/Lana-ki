import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def generate_sellable_content(topic, content_type):
    prompts = {
        "ebook": f"Erstelle ein 10-Kapitel Ebook über {topic}. Jedes Kapitel 500 Wörter.",
        "course": f"Erstelle einen Online-Kurs über {topic} mit 5 Modulen und Übungen.",
        "templates": f"Erstelle 10 verkaufbare Templates für {topic}.",
        "scripts": f"Erstelle 5 verkaufbare Skripte/Tools für {topic}."
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": prompts[content_type]}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            # Speichere verkaufbaren Content
            filename = f"sellable_{content_type}_{topic.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ {content_type.upper()} für '{topic}' erstellt: {filename}")
            print(f"💰 Verkaufspreis Empfehlung: €{get_price_suggestion(content_type)}")
            return filename
        else:
            print(f"❌ Fehler: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return None

def get_price_suggestion(content_type):
    prices = {
        "ebook": "19.99",
        "course": "97.00", 
        "templates": "29.99",
        "scripts": "49.99"
    }
    return prices.get(content_type, "19.99")

if __name__ == "__main__":
    topics = ["Affiliate Marketing", "Krypto Trading", "AI Tools", "Online Business"]
    types = ["ebook", "course", "templates", "scripts"]
    
    for topic in topics:
        for content_type in types:
            generate_sellable_content(topic, content_type)
            print("-" * 50)
