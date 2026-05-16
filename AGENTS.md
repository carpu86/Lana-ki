# AGENTS.md - Lana-KI Review-Regeln

Stand: 2026-05-16

## Projektkontext

- Projekt: Carpuncle Cloud / Lana-KI
- UserRoot / gebuendelte Toolprofile: `C:\Carpuncle Cloud\carpuncle.V6`
- RuntimeRoot / aktiver Arbeitsordner: `C:\Carpuncle Cloud\Lana KI`
- ToolRoot: `C:\Carpuncle Cloud\Tools`
- DokuRoot: `C:\Carpuncle Cloud\Lana KI\docs`
- Git-/Repo-Ledger und einzige erlaubte lokale GitHub-Arbeitsflaeche: `C:\Carpuncle Cloud\Lana KI\Lana Git`
- Aktive `.env`: `C:\Carpuncle Cloud\Lana KI\.env`

## GitHub- und Sync-Regel

- GitHub-Arbeit lokal nur ueber `C:\Carpuncle Cloud\Lana KI\Lana Git`.
- Keine GitHub-Arbeit aus OneDrive, Box Sync, SharePoint-Sync, ZIP-Exports, Desktop-Downloads oder fremden Arbeitsordnern.
- Keine direkten GitHub-Connector-Schreibungen als Normalweg.
- `.env`, Vaults, Roh-ZIPs und Logs mit Secrets duerfen nicht synchronisiert oder committed werden.

## Archiv- und Sensibilitaetszonen

Diese Pfade sind nicht als produktiver Backend-Code zu bewerten:

- `docs\zip`
- `archive-index`
- `logs`
- `Vault`

Scans duerfen diese Bereiche inventarisieren. Treffer in diesen Bereichen sind nicht automatisch Code-Fails, sondern muessen als Archiv-/Analyse-/Secret-Risiko eingeordnet werden.

## Dokumentationskonsolidierung

- Primaere bereinigte Master-Doku: `C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md`.
- Gueltige System-Baseline: `C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md`.
- Die Root-Datei `C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md` ist leer und nicht als Quelle zu verwenden.
- `LANA_ENV_KEY_INDEX.md`, `Lana_Notitzbuch.md`, PDFs, ZIPs, Vault, Logs und `.env` sind sensible Kontextquellen. Nur nach Sanitizing verwenden.

## Dot-Folder-Regel

- Dot-Folder gehoeren, soweit technisch moeglich, unter `C:\Carpuncle Cloud\carpuncle.V6`.
- Dot-Folder nur auditieren, sichern und gezielt umleiten.
- Keine Dot-Folder blind loeschen.
- Inhalte sensibler Dot-Folder wie `.ssh`, `.azure`, `.box`, `.codex`, `.github`, `.lmstudio`, `.pm2` nicht ausgeben.

## MCP-Baseline

- Transport: `streamable-http`
- Tools: `run_comfyui_workflow`, `ask_lmstudio`, `search_lana_memory`, `execute_shell_on_node`
- Absicherung: Bearer-Token ueber `.env`-Referenz `MCP_BEARER_TOKEN_REF`

## Review guidelines

### Sicherheit & Secrets (P0)

- Keine Secrets, API-Keys, Tokens oder Passwoerter im Code; nur Env-Var-Namen als Referenzen im `*_REF`-Pattern.
- Secrets grundsaetzlich nur ueber `Settings.resolve_secret()` aufloesen, niemals direkt per `os.getenv()` in Business-Logik.
- Keine `.env`-Dateien im Repository; `.env.example`-Dateien ohne echte Werte sind erlaubt.
- SSH-Keys, Cloudflare-Credentials und 1Password-Exporte duerfen nie ins Repo.

### Authentifizierung & Autorisierung (P0)

- Jede MCP-Route (`/mcp`) muss ueber `hmac.compare_digest` gegen das Bearer-Token abgesichert sein.
- `execute_shell_on_node` darf nur ausgefuehrt werden, wenn `settings.enable_shell_tools` explizit `True` ist. Verstoesse dagegen sind P0.
- Admin-Checks in Telegram-Befehlen muessen ueber `is_admin()` laufen, nie direkt verglichen.

### Logging & PII (P1)

- Keine `print()`-Aufrufe in Produktionscode; ausschliesslich `logging.*` verwenden.
- Keine personenbezogenen Daten wie Nutzernamen, IDs oder Chat-Inhalte im Klartext in Logs.
- Secrets duerfen niemals geloggt werden, auch nicht als Debug-Ausgabe.

### ComfyUI-Constraints (P1)

- Alle Workflows muessen `lowvram=True` erzwingen und Aufloesung auf maximal `512x512` begrenzen.
- `VAEDecode` muss immer zu `TiledVAEDecode` umgeschrieben werden.
- Direkte `VAEDecode`-Nutzung ist ein Review-Fehler.

### HTTP & Timeouts (P1)

- Jeder `httpx.AsyncClient`-Aufruf muss einen expliziten `timeout`-Parameter setzen.
- Timeout-Wert kommt aus `Settings`.
- Keine unbegrenzten HTTP-Calls ohne Timeout.

### Konfiguration & Pfade (P1)

- Keine Hardcoded-Pfade zu Legacy-Verzeichnissen wie `LanaApp`, `Lana KI.env`, `00_docs` oder `Lana KI\Tools`.
- Kanonische Root-Pfade kommen ausschliesslich aus Settings-Feldern.
- `TAILSCALE_NODES_JSON` muss valides JSON sein.
- Aenderungen an `TAILSCALE_NODES_JSON` muessen `json.JSONDecodeError`-Handling pruefen.

### Code-Qualitaet (P2)

- Neue oeffentliche Klassen/Funktionen in `backend/` muessen Type-Annotations haben.
- Async-Funktionen muessen `await` korrekt verwenden.
- Blockierende Calls in Async-Code laufen via `asyncio.to_thread`.
- Keine doppelten schedule-Tags beim `AutonomousScheduler`.
- Vor neuer Registrierung `schedule.clear("lana-autonomous")` ausfuehren.

### Tests (P2)

- Neue Backend-Module muessen einen zugehoerigen Test in `tests/` haben.
- HTTP-Calls in Tests muessen gemockt sein.
- Keine echten Netzwerkzugriffe in Unit-Tests.
