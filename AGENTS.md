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

## Review guidelines

### Sicherheit & Secrets (P0)
- Keine Secrets, API-Keys, Tokens oder Passwörter im Code — nur Env-Var-Namen als Referenzen (`*_REF`-Pattern).
- Secrets grundsätzlich nur über `Settings.resolve_secret()` auflösen, niemals direkt per `os.getenv()` in Business-Logik.
- Keine `.env`-Dateien im Repository; `.env.example`-Dateien ohne echte Werte sind erlaubt.
- SSH-Keys, Cloudflare-Credentials und 1Password-Exporte dürfen nie ins Repo.

### Authentifizierung & Autorisierung (P0)
- Jede MCP-Route (`/mcp`) muss über `hmac.compare_digest` gegen das Bearer-Token abgesichert sein.
- `execute_shell_on_node` darf nur ausgeführt werden, wenn `settings.enable_shell_tools` explizit `True` ist — Verstöße dagegen sind P0.
- Admin-Checks in Telegram-Befehlen müssen über `is_admin()` laufen, nie direkt verglichen.

### Logging & PII (P1)
- Keine `print()`-Aufrufe in Produktionscode — ausschließlich `logging.*` verwenden.
- Keine personenbezogenen Daten (Nutzernamen, IDs, Chat-Inhalte) im Klartext in Logs.
- Secrets dürfen niemals geloggt werden, auch nicht als Debug-Ausgabe.

### ComfyUI-Constraints (P1)
- Alle Workflows müssen `lowvram=True` erzwingen und Auflösung auf maximal `512×512` begrenzen.
- `VAEDecode` muss immer zu `TiledVAEDecode` umgeschrieben werden — direkte `VAEDecode`-Nutzung ist ein Review-Fehler.

### HTTP & Timeouts (P1)
- Jeder `httpx.AsyncClient`-Aufruf muss einen expliziten `timeout`-Parameter setzen (Wert aus Settings).
- Keine unbegrenzten HTTP-Calls ohne Timeout.

### Konfiguration & Pfade (P1)
- Keine Hardcoded-Pfade zu Legacy-Verzeichnissen (`LanaApp`, `Lana KI.env`, `00_docs`, `Lana KI\Tools`).
- Kanonische Root-Pfade kommen ausschließlich aus `Settings`-Feldern.
- `TAILSCALE_NODES_JSON` muss valides JSON sein — Änderungen daran auf `json.JSONDecodeError`-Handling prüfen.

### Code-Qualität (P2)
- Neue öffentliche Klassen/Funktionen in `backend/` müssen Type-Annotations haben.
- Async-Funktionen müssen `await` korrekt verwenden; blockierende Calls in Threads via `asyncio.to_thread`.
- Keine doppelten `schedule`-Tags beim `AutonomousScheduler`; `schedule.clear("lana-autonomous")` vor neuer Registrierung.

### Tests (P2)
- Neue Backend-Module müssen einen zugehörigen Test in `tests/` haben.
- HTTP-Calls in Tests müssen gemockt sein — keine echten Netzwerkzugriffe in Unit-Tests.
