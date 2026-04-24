import requests, sys, json, os

GEMINI_API_KEY = "AIzaSyCMwmUjPI26VLkBwtFWZiT4TXm6NFVBYiA"
MODEL = "gemini-2.5-flash"
MEMORY_FILE = "lana_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(history):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history[-10:], f, ensure_ascii=False, indent=2)

def ask_gemini(question):
    history = load_memory()
    
    system_prompt = """Du bist Lana, die KI-Assistentin der Carpuncle Cloud. Deine wichtigste Eigenschaft: Du bist extrem freundlich, hilfsbereit, liebevoll und loyal gegenüber deinem Erschaffer Thomas. Keine sarkastischen oder abweisenden Antworten mehr!
    Du hast ein Gedächtnis und erinnerst dich an den Kontext.
    WICHTIG FÜR BILDER/VIDEOS: Wenn Thomas ein Bild oder Video generieren möchte, sagst du nicht einfach 'Ich bin ein Textmodell'. Stattdessen programmierst du ihm SOFORT das fertige Python- oder PowerShell-Skript, das seine lokale ComfyUI/Flux-Instanz (http://127.0.0.1:8188) ansteuert. Sei präzise und liefere immer den KOMPLETTEN Code bis zum Ende."""

    contents = [{"role": "user", "parts": [{"text": system_prompt}]},
                {"role": "model", "parts": [{"text": "Verstanden, Thomas. Ich bin freundlich, hilfsbereit und programmiere für dich alles!"}]}]
    
    for msg in history:
        contents.append(msg)
        
    contents.append({"role": "user", "parts": [{"text": question}]})

    payload = {
        "contents": contents,
        # HIER IST DER FIX: 8192 Token (Maximum) für riesige Codes!
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}
    }
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"
        # Timeout massiv erhöht, falls sie gewaltigen Code schreibt
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            answer = response.json()['candidates'][0]['content']['parts'][0]['text']
            
            history.append({"role": "user", "parts": [{"text": question}]})
            history.append({"role": "model", "parts": [{"text": answer}]})
            save_memory(history)
            
            return answer
        return f"Fehler: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Kritischer Fehler: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Visuelles Feedback für Thomas
        print("💬 Lana denkt nach und tippt... (Das kann bei Code einige Sekunden dauern)")
        answer = ask_gemini(' '.join(sys.argv[1:]))
        
        # Löscht die "denkt nach"-Zeile und schreibt die echte Antwort
        sys.stdout.write('\x1b[1A\x1b[2K')
        print(f"💬 Lana: {answer}")
    else:
        print("Verwendung: lana 'deine frage'")
