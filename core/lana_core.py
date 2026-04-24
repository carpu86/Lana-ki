import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests

ROOT = Path(r"C:\Carpuncle Cloud\LanaApp")
ENV_FILE = ROOT / ".env"
DB_FILE = ROOT / "data" / "lana.db"
LOG_FILE = ROOT / "logs" / "lana.log"

load_dotenv(ENV_FILE)

def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scheduler_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            name TEXT NOT NULL,
            cron TEXT NOT NULL,
            action TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.commit()
    return conn

def save_event(event_type: str, payload: dict):
    conn = db()
    conn.execute(
        "INSERT INTO events (created_at, event_type, payload) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), event_type, json.dumps(payload, ensure_ascii=False))
    )
    conn.commit()
    conn.close()

def set_memory(key: str, value: str):
    conn = db()
    conn.execute(
        "INSERT INTO memory (created_at, key, value) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), key, value)
    )
    conn.commit()
    conn.close()

def get_memory():
    conn = db()
    rows = conn.execute("""
        SELECT key, value, created_at
        FROM memory
        ORDER BY id DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return [{"key": r[0], "value": r[1], "created_at": r[2]} for r in rows]

def add_task(title: str, details: str, status: str = "open"):
    conn = db()
    conn.execute(
        "INSERT INTO tasks (created_at, title, status, details) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), title, status, details)
    )
    conn.commit()
    conn.close()

def list_tasks():
    conn = db()
    rows = conn.execute("""
        SELECT id, created_at, title, status, details
        FROM tasks
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()
    conn.close()
    return [
        {"id": r[0], "created_at": r[1], "title": r[2], "status": r[3], "details": r[4]}
        for r in rows
    ]

def add_scheduler_job(name: str, cron: str, action: str):
    conn = db()
    conn.execute(
        "INSERT INTO scheduler_jobs (created_at, name, cron, action, active) VALUES (?, ?, ?, ?, 1)",
        (datetime.now().isoformat(), name, cron, action)
    )
    conn.commit()
    conn.close()

def list_scheduler_jobs():
    conn = db()
    rows = conn.execute("""
        SELECT id, created_at, name, cron, action, active
        FROM scheduler_jobs
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()
    conn.close()
    return [
        {"id": r[0], "created_at": r[1], "name": r[2], "cron": r[3], "action": r[4], "active": bool(r[5])}
        for r in rows
    ]

def get_env(name: str, default: str = ""):
    return os.getenv(name, default)

def call_openrouter(prompt: str) -> str:
    api_key = get_env("OPENROUTER_API_KEY") or get_env("Openrouter")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY fehlt")

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:7861",
            "X-Title": "Lana Local"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Du bist Lana, ein lokaler präziser Assistent."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        },
        timeout=60
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]

def call_groq(prompt: str) -> str:
    api_key = get_env("GROQ_API_KEY") or get_env("Groq")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY fehlt")

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Du bist Lana, ein lokaler präziser Assistent."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        },
        timeout=60
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]

def call_gemini(prompt: str) -> str:
    api_key = (
        get_env("GEMINI_API_KEY") or
        get_env("Gemini") or
        get_env("GEMINI_API_KEY_DEFAULT") or
        get_env("GEMINI_API_KEY_NEW")
    )
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY fehlt")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    r = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": [
                {
                    "parts": [
                        {"text": "Du bist Lana, ein lokaler präziser Assistent."},
                        {"text": prompt}
                    ]
                }
            ]
        },
        timeout=60
    )
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

def call_llm(prompt: str) -> str:
    providers = [
        ("openrouter", call_openrouter),
        ("groq", call_groq),
        ("gemini", call_gemini),
    ]

    errors = []

    for name, fn in providers:
        try:
            text = fn(prompt)
            save_event("llm_call", {"provider": name, "prompt": prompt, "response": text})
            return text
        except Exception as e:
            err = f"{name}: {str(e)}"
            log(err)
            errors.append(err)

    raise RuntimeError(" | ".join(errors))
