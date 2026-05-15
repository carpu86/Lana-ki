# ⚙️ LANA‑KI – Backend

Dieses Verzeichnis enthält jetzt den produktiven Lana-KI-Backend-Stack.

## Struktur

- `backend/main.py` – FastAPI Orchestrator mit `/health`, `/status`, `/v1/chat`
- `backend/config.py` – `.env`-Loading via `python-dotenv` + `pydantic-settings`
- `backend/router/` – Bridges für LM Studio, ComfyUI, Gemini und Routing
- `backend/memory/` – SQLite-Memory mit JSON-Snapshots
- `backend/mcp/` – abgesicherter MCP-Server und Tool-Registry
- `backend/agents/` – Lana, Lia und autonomer Scheduler
- `backend/bots/` – Telegram- und Discord-Bot-Integrationen

## Wichtige Regeln

- Keine Secrets im Repository
- Nur Logging, keine `print()`-Ausgaben
- ComfyUI-Workflows werden auf `lowvram=True`, `TiledVAEDecode` und max. `512x512` begrenzt
- Startup validiert kritische Runtime-Werte klar und früh
