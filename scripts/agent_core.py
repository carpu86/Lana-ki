import os
import json
import time
import uuid
import subprocess
from typing import List, Dict

import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv("/home/carpu/LanaApp/.env")
load_dotenv("C:/Carpuncle Cloud/LanaApp/.env")

APP = FastAPI(title="Lana Agent Core")

LOCAL_LLM_ENDPOINT = os.getenv("LOCAL_LLM_ENDPOINT", "http://127.0.0.1:1234/v1").rstrip("/")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "qwen2.5-7b-instruct")
SYSTEM_PROMPT = os.getenv("LANA_SYSTEM_PROMPT", "Du bist Lana. Antworte auf Deutsch.")
MEMORY_PATH = os.getenv("LANA_AGENT_MEMORY", "/home/carpu/LanaApp/data/agent_memory.jsonl")
WORKSPACE = os.getenv("LANA_AGENT_WORKSPACE", "/home/carpu/LanaApp/workspace_agent")
BRAIN_HOST = os.getenv("LANA_BRAIN_SSH_HOST", "")
PORT = int(os.getenv("LANA_AGENT_PORT", "8100"))

os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
os.makedirs(WORKSPACE, exist_ok=True)

ALLOWED_LOCAL_SHELL_PREFIXES = (
    "ls", "pwd", "cat", "head", "tail", "grep", "find",
    "python", "python3",
    "git status", "git diff", "git log",
    "mkdir", "cp", "mv", "echo", "sed", "awk"
)

ALLOWED_REMOTE_SHELL_PREFIXES = (
    "ls", "pwd", "cat", "head", "tail", "grep", "find",
    "python", "python3",
    "git status", "git diff", "git log",
    "mkdir", "cp", "mv", "echo", "sed", "awk",
    "systemctl status", "journalctl -n", "df -h", "free -h", "nproc", "uname -a"
)

class AgentRequest(BaseModel):
    prompt: str
    allow_web: bool = True
    allow_code: bool = True
    allow_shell: bool = True
    max_steps: int = 5

def read_memory(last_n: int = 12) -> List[Dict[str, str]]:
    if not os.path.exists(MEMORY_PATH):
        return []
    out = []
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        lines = [x.strip() for x in f.readlines() if x.strip()]
    for line in lines[-last_n:]:
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def append_memory(role: str, content: str) -> None:
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "role": role,
        "content": content
    }
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

async def llm_chat(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 900) -> str:
    payload = {
        "model": LOCAL_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    async with httpx.AsyncClient(timeout=180.0) as client:
        r = await client.post(f"{LOCAL_LLM_ENDPOINT}/chat/completions", json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

async def search_web(query: str) -> str:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        r = await client.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
        )
        r.raise_for_status()
        data = r.json()

    parts = []
    if data.get("AbstractText"):
        parts.append(data["AbstractText"])

    for item in data.get("RelatedTopics", [])[:5]:
        if isinstance(item, dict):
            txt = item.get("Text")
            if txt:
                parts.append(txt)

    if not parts:
        return "Keine brauchbaren Web-Ergebnisse."

    return "\n".join(parts[:6])

def run_python_local(code: str) -> str:
    temp_name = os.path.join(WORKSPACE, f"agent_{uuid.uuid4().hex}.py")
    with open(temp_name, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        result = subprocess.run(
            ["python3", temp_name],
            capture_output=True,
            text=True,
            timeout=90,
            cwd=WORKSPACE
        )
        return (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    except subprocess.TimeoutExpired:
        return "Python-Timeout."
    except Exception as e:
        return f"Python-Fehler: {e}"

def shell_allowed(cmd: str, allowed_prefixes) -> bool:
    c = cmd.strip().lower()
    return any(c.startswith(prefix) for prefix in allowed_prefixes)

def run_shell_local(cmd: str) -> str:
    if not shell_allowed(cmd, ALLOWED_LOCAL_SHELL_PREFIXES):
        return "Lokaler Shell-Befehl nicht erlaubt."
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WORKSPACE
        )
        return (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    except subprocess.TimeoutExpired:
        return "Lokaler Shell-Timeout."
    except Exception as e:
        return f"Lokaler Shell-Fehler: {e}"

def run_shell_brain(cmd: str) -> str:
    if not BRAIN_HOST:
        return "BRAIN_HOST fehlt."
    if not shell_allowed(cmd, ALLOWED_REMOTE_SHELL_PREFIXES):
        return "Remote-Shell-Befehl nicht erlaubt."
    try:
        result = subprocess.run(
            ["ssh", BRAIN_HOST, cmd],
            capture_output=True,
            text=True,
            timeout=90
        )
        return (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    except subprocess.TimeoutExpired:
        return "Brain-Shell-Timeout."
    except Exception as e:
        return f"Brain-Shell-Fehler: {e}"

TOOL_SCHEMA = """
Verfügbare Tools:
1. search_web(query: string)
2. run_python_local(code: string)
3. run_shell_local(cmd: string)
4. run_shell_brain(cmd: string)

Regeln:
- Nutze run_shell_brain für Remote-Linux-Checks oder freie Brain-Leistung.
- Nutze run_python_local für kleine Agent-Skripte auf dem Laptop.
- Nutze run_shell_local für Dateiverwaltung im Agent-Workspace.
- Antworte bei Tool-Nutzung EXAKT als JSON in EINER Zeile.

Beispiele:
{"tool":"search_web","args":{"query":"fastapi health endpoint example"}}
{"tool":"run_python_local","args":{"code":"print('hallo')"}}
{"tool":"run_shell_local","args":{"cmd":"ls -la"}}
{"tool":"run_shell_brain","args":{"cmd":"python3 --version"}}

Wenn du fertig bist, antworte normal auf Deutsch.
"""

def try_parse_tool_call(text: str):
    text = text.strip()
    if not text.startswith("{"):
        return None
    try:
        data = json.loads(text)
        if "tool" in data and "args" in data:
            return data
    except Exception:
        return None
    return None

@APP.get("/health")
async def health():
    return {
        "ok": True,
        "service": "lana-agent-core",
        "model": LOCAL_MODEL,
        "workspace": WORKSPACE,
        "memory_path": MEMORY_PATH,
        "brain_host": BRAIN_HOST,
        "llm_endpoint": LOCAL_LLM_ENDPOINT
    }

@APP.post("/agent")
async def agent(req: AgentRequest):
    try:
        memory = read_memory(12)

        messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + TOOL_SCHEMA}]
        for m in memory:
            if m.get("role") in ("user", "assistant"):
                messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": req.prompt})

        final_answer = None
        steps = max(1, min(req.max_steps, 8))

        for _ in range(steps):
            reply = await llm_chat(messages, temperature=0.2, max_tokens=900)
            tool_call = try_parse_tool_call(reply)

            if not tool_call:
                final_answer = reply
                break

            tool = tool_call["tool"]
            args = tool_call.get("args", {})

            if tool == "search_web" and req.allow_web:
                result = await search_web(str(args.get("query", "")))
            elif tool == "run_python_local" and req.allow_code:
                result = run_python_local(str(args.get("code", "")))
            elif tool == "run_shell_local" and req.allow_shell:
                result = run_shell_local(str(args.get("cmd", "")))
            elif tool == "run_shell_brain" and req.allow_shell:
                result = run_shell_brain(str(args.get("cmd", "")))
            else:
                result = f"Tool nicht erlaubt oder unbekannt: {tool}"

            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "TOOL_RESULT:\n" + result})

        if final_answer is None:
            final_answer = "Ich konnte die Aufgabe nicht sauber abschließen."

        append_memory("user", req.prompt)
        append_memory("assistant", final_answer)

        return {"ok": True, "answer": final_answer}
    except Exception as e:
        return {"ok": False, "answer": f"Agent-Fehler: {type(e).__name__}: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(APP, host="0.0.0.0", port=PORT)
