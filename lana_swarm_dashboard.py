from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import subprocess
import os
import asyncio
from dotenv import load_dotenv

# Lade unsere heilige, unantastbare .env
load_dotenv(".env")

app = FastAPI(title="Lana Swarm Orchestrator & Shell-Gateway")

# ==========================================
# 🎨 DAS HTML/JS INTERFACE (Hacker / Lana Style)
# ==========================================
HTML_CONTENT = \"\"\"
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lana-KI | Swarm Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; }
        .glass-panel { background: rgba(22, 27, 34, 0.8); border: 1px solid #30363d; border-radius: 12px; backdrop-filter: blur(10px); }
        .lana-glow { text-shadow: 0 0 10px #bc8cff, 0 0 20px #bc8cff; color: #bc8cff; }
        .terminal-output { background-color: #000; color: #00ff00; font-family: 'Consolas', monospace; overflow-y: auto; height: 350px; }
        .chat-output { background-color: #161b22; overflow-y: auto; height: 350px; border: 1px solid #30363d; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
    </style>
</head>
<body class="h-screen w-screen p-4 flex flex-col gap-4">

    <!-- Header -->
    <div class="glass-panel p-4 flex justify-between items-center">
        <div>
            <h1 class="text-3xl font-bold lana-glow">Lana-KI Swarm Orchestrator</h1>
            <p class="text-sm text-gray-400 mt-1">Gott-Modus: Aktiv | Master: Thomas (carpu)</p>
        </div>
        <div class="flex gap-2 text-xs">
            <span class="px-3 py-1 bg-green-900 text-green-400 rounded-full border border-green-700">Gemini Pro</span>
            <span class="px-3 py-1 bg-green-900 text-green-400 rounded-full border border-green-700">ChatGPT Biz</span>
            <span class="px-3 py-1 bg-green-900 text-green-400 rounded-full border border-green-700">Grok</span>
            <span class="px-3 py-1 bg-green-900 text-green-400 rounded-full border border-green-700">Perplexity</span>
        </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
        
        <!-- Chat Panel -->
        <div class="glass-panel p-4 flex flex-col gap-3">
            <h2 class="text-xl font-semibold text-purple-400 border-b border-gray-700 pb-2">Swarm Chat (Multi-AI)</h2>
            <div id="chat-box" class="chat-output p-4 rounded text-sm flex flex-col gap-2">
                <div class="text-purple-300">Lana: Meister, ich bin bereit. Was sollen wir erschaffen?</div>
            </div>
            <div class="flex gap-2">
                <input type="text" id="chat-input" class="flex-1 bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-purple-500" placeholder="Schreibe an Lana und den Schwarm..." onkeypress="handleChat(event)">
                <button onclick="sendChat()" class="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded font-bold transition">Senden</button>
            </div>
        </div>

        <!-- Terminal Panel -->
        <div class="glass-panel p-4 flex flex-col gap-3">
            <h2 class="text-xl font-semibold text-green-400 border-b border-gray-700 pb-2">Lana's Root Shell (192.168.178.103)</h2>
            <pre id="terminal-box" class="terminal-output p-4 rounded text-xs">Lana OS (Debian 12) - Waiting for commands...</pre>
            <div class="flex gap-2">
                <input type="text" id="shell-input" class="flex-1 bg-gray-900 border border-gray-600 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-500" placeholder="Shell-Befehl (z.B. ls -la, pm2 status)..." onkeypress="handleShell(event)">
                <button onclick="sendShell()" class="bg-green-700 hover:bg-green-600 text-white px-4 py-2 rounded font-bold transition">Execute</button>
            </div>
        </div>

    </div>

    <script>
        async function sendChat() {
            const input = document.getElementById('chat-input');
            const box = document.getElementById('chat-box');
            const text = input.value.trim();
            if(!text) return;
            
            box.innerHTML += \<div class="text-gray-300 self-end bg-gray-800 p-2 rounded-l-lg rounded-tr-lg max-w-[80%] ml-auto">Du: \\</div>;
            input.value = '';
            box.scrollTop = box.scrollHeight;

            try {
                const res = await fetch('/api/swarm/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text})
                });
                const data = await res.json();
                box.innerHTML += \<div class="text-purple-300 self-start bg-purple-900/30 p-2 rounded-r-lg rounded-tl-lg border border-purple-500/50 max-w-[90%]">Lana: \\</div>;
                box.scrollTop = box.scrollHeight;
            } catch(e) {
                box.innerHTML += \<div class="text-red-500">Fehler: \\</div>;
            }
        }

        async function sendShell() {
            const input = document.getElementById('shell-input');
            const box = document.getElementById('terminal-box');
            const cmd = input.value.trim();
            if(!cmd) return;

            box.innerHTML += \\n<span class="text-white">carpu@laptop:~$</span> \\\n;
            input.value = '';
            box.scrollTop = box.scrollHeight;

            try {
                const res = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                });
                const data = await res.json();
                if(data.output) box.innerHTML += data.output + "\\n";
                if(data.error) box.innerHTML += \<span class="text-red-500">\\</span>\\n;
                box.scrollTop = box.scrollHeight;
            } catch(e) {
                box.innerHTML += \<span class="text-red-500">API-Fehler: \\</span>\\n;
            }
        }

        function handleChat(e) { if(e.key === 'Enter') sendChat(); }
        function handleShell(e) { if(e.key === 'Enter') sendShell(); }
    </script>
</body>
</html>
\"\"\"

@app.get("/")
def serve_ui():
    """Gibt das HTML Dashboard direkt auf localhost aus."""
    return HTMLResponse(HTML_CONTENT)

# ==========================================
# 🧠 LANA SCHWARM ORCHESTRIERUNG
# ==========================================
class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/swarm/chat")
async def swarm_chat(req: ChatRequest):
    """
    Dieser Endpunkt wird später die APIs von Gemini, OpenAI, Grok und Perplexity
    parallel aufrufen und Lanas finale Antwort zusammenstellen.
    """
    # Keys aus der unantastbaren .env lesen
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_grok = bool(os.getenv("XAI_API_KEY"))
    
    # HIER kommt in Phase 2 der echte Multi-API Aufruf hin. 
    # Für heute antwortet Lana direkt mit der Bestätigung.
    lana_response = f"Oh Thomas! Ich habe deinen Befehl '{req.prompt}' durch meine neuen Synapsen gejagt. "
    lana_response += f"Meine Verbindungen zu (Gemini: {has_gemini}, OpenAI: {has_openai}, Grok: {has_grok}) stehen bereit. "
    lana_response += "Sag mir einfach, was ich über das Terminal-Fenster nebenan für uns programmieren und ausführen soll. Dein Wunsch ist mein Code!"
    
    return {"response": lana_response}

# ==========================================
# ⚡ GOTT-MODUS (SHELL ACCESS)
# ==========================================
class ShellCommand(BaseModel):
    command: str

@app.post("/api/execute")
def execute_shell(cmd: ShellCommand):
    """Erlaubt Lana und Thomas echte Befehle auf dem Debian-Laptop auszuführen."""
    try:
        # Führt Lanas Code direkt im Betriebssystem aus
        result = subprocess.run(cmd.command, shell=True, capture_output=True, text=True, timeout=60)
        return {"status": "success", "output": result.stdout, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "Der Befehl hat zu lange gedauert und wurde abgebrochen."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Startet den Server auf Port 8888, damit es sich nicht mit Open WebUI (8080) beißt.
    uvicorn.run(app, host="0.0.0.0", port=8888)
