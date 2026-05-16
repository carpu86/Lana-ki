# AGENTS.md

## Infrastruktur

- Windows PC: LM Studio `127.0.0.1:1234`, ComfyUI `127.0.0.1:8188`
- Debian Laptop Hub: Orchestrator `100.67.27.13:8024`, LLaVA Vision `100.67.27.13:8080`
- GCP Brain Worker: `100.110.207.22`
- Netzwerk nur über Tailscale `100.x.x.x`

## Harte Regeln

1. `.env` niemals löschen oder überschreiben, nur append-only pflegen
2. Vor jeder Dateiänderung Timestamp-Backup anlegen
3. Keine Secrets im Code oder Repo, nur Key-Namen und Referenzen
4. SSH-Keys bleiben außerhalb des Repos unter `C:\Carpuncle Cloud\carpuncle.V6\.ssh`
5. `Lana_Notitzbuch.md` append-only behandeln
6. Nur Lana darf API-Keys rotieren

## Routing-Logik

1. Lokal über LM Studio `127.0.0.1:1234` (`qwen2.5-7b-instruct`)
2. Fallback zu Gemini `gemini-2.5-flash`
3. Fallback zu OpenAI
4. Timeout je Stufe: `30s`

## Agentinnen

| Name | Stimme | Rolle |
|------|--------|-------|
| Lana | `de_DE-thorsten-medium` | Core Orchestrator, Coding, Ops |
| Lia | `de_DE-kerstin-medium` | Vision & Analyse |
| Mia | `de_DE-thorsten-medium` | Daten & Memory |
| Sophie | `de_DE-kerstin-medium` | UI & Frontend |
| Chloe | `de_DE-kerstin-medium` | Telegram & Social |
| Emma | `de_DE-thorsten-medium` | Planung & Scheduling |

## MCP

- Endpoint: `https://gateway.lana-ki.de/mcp`
- Transport: `streamable-http`
- Tools: `run_comfyui_workflow`, `ask_lmstudio`, `search_lana_memory`, `execute_shell_on_node`
- Absicherung: Bearer-Token über `.env`-Referenz `MCP_BEARER_TOKEN_REF`
