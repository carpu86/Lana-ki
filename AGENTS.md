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

AGENTS.md - Lana-KI Review-Regeln
Stand: 2026-05-16

Projektkontext
Projekt: Carpuncle Cloud / Lana-KI
UserRoot / gebuendelte Toolprofile: C:\Carpuncle Cloud\carpuncle.V6
RuntimeRoot / aktiver Arbeitsordner: C:\Carpuncle Cloud\Lana KI
ToolRoot: C:\Carpuncle Cloud\Tools
DokuRoot: C:\Carpuncle Cloud\Lana KI\docs
Git-/Repo-Ledger und einzige erlaubte lokale GitHub-Arbeitsflaeche: C:\Carpuncle Cloud\Lana KI\Lana Git
Aktive .env: C:\Carpuncle Cloud\Lana KI\.env
GitHub- und Sync-Regel
GitHub-Arbeit lokal nur ueber C:\Carpuncle Cloud\Lana KI\Lana Git.
Keine GitHub-Arbeit aus OneDrive, Box Sync, SharePoint-Sync, ZIP-Exports, Desktop-Downloads oder fremden Arbeitsordnern.
Keine direkten GitHub-Connector-Schreibungen als Normalweg.
.env, Vaults, Roh-ZIPs und Logs mit Secrets duerfen nicht synchronisiert oder committed werden.
Archiv- und Sensibilitaetszonen
Diese Pfade sind nicht als produktiver Backend-Code zu bewerten:

docs\zip
archive-index
logs
Vault
Scans duerfen diese Bereiche inventarisieren. Treffer in diesen Bereichen sind nicht automatisch Code-Fails, sondern muessen als Archiv-/Analyse-/Secret-Risiko eingeordnet werden.

Dokumentationskonsolidierung
Primaere bereinigte Master-Doku: C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md.
Gueltige System-Baseline: C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md.
Die Root-Datei C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md ist leer und nicht als Quelle zu verwenden.
LANA_ENV_KEY_INDEX.md, Lana_Notitzbuch.md, PDFs, ZIPs, Vault, Logs und .env sind sensible Kontextquellen. Nur nach Sanitizing verwenden.
Dot-Folder-Regel
Dot-Folder gehoeren, soweit technisch moeglich, unter C:\Carpuncle Cloud\carpuncle.V6.
Dot-Folder nur auditieren, sichern und gezielt umleiten.
Keine Dot-Folder blind loeschen.
Inhalte sensibler Dot-Folder wie .ssh, .azure, .box, .codex, .github, .lmstudio, .pm2 nicht ausgeben.
MCP-Baseline
Transport: streamable-http
Tools: run_comfyui_workflow, ask_lmstudio, search_lana_memory, execute_shell_on_node
Absicherung: Bearer-Token ueber .env-Referenz MCP_BEARER_TOKEN_REF
Review guidelines
Sicherheit & Secrets (P0)
Keine Secrets, API-Keys, Tokens oder Passwoerter im Code; nur Env-Var-Namen als Referenzen im *_REF-Pattern.
Secrets grundsaetzlich nur ueber Settings.resolve_secret() aufloesen, niemals direkt per os.getenv() in Business-Logik.
Keine .env-Dateien im Repository; .env.example-Dateien ohne echte Werte sind erlaubt.
SSH-Keys, Cloudflare-Credentials und 1Password-Exporte duerfen nie ins Repo.
Authentifizierung & Autorisierung (P0)
Jede MCP-Route (/mcp) muss ueber hmac.compare_digest gegen das Bearer-Token abgesichert sein.
execute_shell_on_node darf nur ausgefuehrt werden, wenn settings.enable_shell_tools explizit True ist. Verstoesse dagegen sind P0.
Admin-Checks in Telegram-Befehlen muessen ueber is_admin() laufen, nie direkt verglichen.
Logging & PII (P1)
Keine print()-Aufrufe in Produktionscode; ausschliesslich logging.* verwenden.
Keine personenbezogenen Daten wie Nutzernamen, IDs oder Chat-Inhalte im Klartext in Logs.
Secrets duerfen niemals geloggt werden, auch nicht als Debug-Ausgabe.
ComfyUI-Constraints (P1)
Alle Workflows muessen lowvram=True erzwingen und Aufloesung auf maximal 512x512 begrenzen.
VAEDecode muss immer zu TiledVAEDecode umgeschrieben werden.
Direkte VAEDecode-Nutzung ist ein Review-Fehler.
HTTP & Timeouts (P1)
Jeder httpx.AsyncClient-Aufruf muss einen expliziten timeout-Parameter setzen.
Timeout-Wert kommt aus Settings.
Keine unbegrenzten HTTP-Calls ohne Timeout.
Konfiguration & Pfade (P1)
Keine Hardcoded-Pfade zu Legacy-Verzeichnissen wie LanaApp, Lana KI.env, 00_docs oder Lana KI\Tools.
Kanonische Root-Pfade kommen ausschliesslich aus Settings-Feldern.
TAILSCALE_NODES_JSON muss valides JSON sein.
Aenderungen an TAILSCALE_NODES_JSON muessen json.JSONDecodeError-Handling pruefen.
Code-Qualitaet (P2)
Neue oeffentliche Klassen/Funktionen in backend/ muessen Type-Annotations haben.
Async-Funktionen muessen await korrekt verwenden.
Blockierende Calls in Async-Code laufen via asyncio.to_thread.
Keine doppelten schedule-Tags beim AutonomousScheduler.
Vor neuer Registrierung schedule.clear("lana-autonomous") ausfuehren.
Tests (P2)
Neue Backend-Module muessen einen zugehoerigen Test in tests/ haben.
HTTP-Calls in Tests muessen gemockt sein.
Keine echten Netzwerkzugriffe in Unit-Tests.
LANA_SYSTEM_BASELINE
Stand: 2026-05-16

Projekt
Name: Carpuncle Cloud / Lana-KI
Hauptsystem: Windows
Shell: PowerShell 7
RuntimeRoot: C:\Carpuncle Cloud\Lana KI
DokuRoot: C:\Carpuncle Cloud\Lana KI\docs
UserRoot: C:\Carpuncle Cloud\carpuncle.V6
ToolRoot: C:\Carpuncle Cloud\Tools
GitHub lokal nur ueber: C:\Carpuncle Cloud\Lana KI\Lana Git
Aktive .env: C:\Carpuncle Cloud\Lana KI\.env
Domains
lana-ki.de: Frontend / Companion-App
gateway.lana-ki.de: Edge / MCP / Connector Plane
carpuncle.de: Backend / Core API
carpuncle.org: Background Sync / Workflows
carpuncle.eu: M365 / Identity / Mail
Nodes
Node A: Hetzner / Public Edge / Cloudflare Tunnel / Gateway / MCP-Routing / Control Plane
Node B: lokaler Windows Desktop / Primary Compute / LM Studio 127.0.0.1:1234 / ComfyUI 127.0.0.1:8188
Node C: RunPod / Burst GPU / On-Demand Heavy Jobs
Node D: Debian Laptop / Admin / Memory / Monitoring / Relay / 192.168.178.101
Node E: GCP / experimentelle temporaere Worker
NAS: FritzBox / Vault / Cold Storage / Backups / offline-first / nur VPN
MCP / Gateway
ChatGPT Custom MCP verbindet sich nicht direkt mit lokalen Diensten.
Oeffentlicher Einstieg: Node A / Gateway.
MCP URL laut Doku: https://gateway.lana-ki.de/mcp
Fallback laut Doku: https://gateway.lana-ki.de/sse
Bearer-Token nur als Secret-Referenz, nicht im Klartext.
Live-Status von Gateway, Tunnel und Endpunkten: unbestaetigt bis Healthcheck.
Quellenstatus
Diese Datei unter docs ist die gueltige System-Baseline.
Die Root-Datei C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md ist leer und nicht als Quelle zu verwenden.
Aeltere P0-Befunde aus importierten Dokumenten bleiben Kontext, bis sie live neu geprueft wurden.
Standard-Diagnose
Test-Path
Get-ChildItem
Get-NetTCPConnection
Get-CimInstance Win32_Process
Get-Content -Tail
Invoke-RestMethod
curl.exe
git status --short nur unter C:\Carpuncle Cloud\Lana KI\Lana Git
Verboten
Secret-Werte ausgeben
.env loeschen, leeren oder blind ueberschreiben
Cloudflare/CAPTCHA/Auth umgehen
P0 rot als Erfolg melden

Lana Sync Note
Stand: 2026-05-16

Root Cause
Chat-, Box-AI-, OneDrive-, SharePoint-, GitHub- und ZIP-Quellen waren verteilt. Zusaetzlich haben Tools Dot-Folder an mehreren Stellen erzeugt, weil viele Programme ohne zentrale HOME-/Profilumleitung in %USERPROFILE%, Projektordner oder den aktuellen Arbeitsordner schreiben.

Fix
Einheitliche lokale Wahrheit:

C:\Carpuncle Cloud\carpuncle.V6
C:\Carpuncle Cloud\Lana KI
C:\Carpuncle Cloud\Tools
GitHub-Arbeit nur ueber:

C:\Carpuncle Cloud\Lana KI\Lana Git
Aktive Doku:

C:\Carpuncle Cloud\Lana KI\docs
C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md
Dot-Folder werden unter C:\Carpuncle Cloud\carpuncle.V6 gebuendelt, soweit technisch moeglich. Keine Dot-Folder blind loeschen.

Konsolidierte Quellenregel
Primaere Master-Doku: C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md
Gueltige System-Baseline: C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md
Root-Datei C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md ist leer und keine Quelle.
LANA_ENV_KEY_INDEX.md, Lana_Notitzbuch.md, PDFs, ZIPs, Vault, Logs und .env sind sensible Kontextquellen und duerfen nicht roh synchronisiert werden.
Testblock
Vor Sync oder GitHub-Aktion:

Test-Path auf die drei Root-Pfade.
Secret-Scan auf Zielartefakte.
GitHub-Pfad muss C:\Carpuncle Cloud\Lana KI\Lana Git sein.

Lana-KI Unified Chatinfos
Stand: 2026-05-16

Zweck
Diese Datei ist der bereinigte zentrale Einstiegspunkt fuer Lana-KI / Carpuncle Cloud. Sie ersetzt keine Rohquellen, sondern fasst den aktuell belegten Projektstand secret-safe zusammen.

Konsolidierungsstand
Konsolidiert am: 2026-05-16
Primaere Quelle: C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md
Aktiver Doku-Ort: C:\Carpuncle Cloud\Lana KI\docs
Gueltige System-Baseline: C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md
Nicht als Quelle verwenden: C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md, weil die Root-Datei aktuell leer ist.
Visuelles Asset: C:\Carpuncle Cloud\Lana KI\docs\lana_logo_192x192.png; nur Logo/Branding, keine Architekturquelle.
Kanonische lokale Quellen
UserRoot / gebuendelte Toolprofile: C:\Carpuncle Cloud\carpuncle.V6
RuntimeRoot: C:\Carpuncle Cloud\Lana KI
ToolRoot: C:\Carpuncle Cloud\Tools
Aktive Doku: C:\Carpuncle Cloud\Lana KI\docs
Lokale Arbeitskopie in dieser Session: T:\Lana KI
Git-/Repo-Ledger und einzige erlaubte GitHub-Arbeitsflaeche: C:\Carpuncle Cloud\Lana KI\Lana Git
Runtime-Konfiguration im aktiven Workspace: C:\Carpuncle Cloud\Lana KI\.env
Hinweis: T:\Lana KI ist in dieser Session nur Spiegel/Arbeitsansicht, nicht neue Projektwahrheit.
Erlaubte RuntimeRoot-Unterordner
C:\Carpuncle Cloud\Lana KI\apps
C:\Carpuncle Cloud\Lana KI\archive-index
C:\Carpuncle Cloud\Lana KI\audit
C:\Carpuncle Cloud\Lana KI\cloudflare
C:\Carpuncle Cloud\Lana KI\config
C:\Carpuncle Cloud\Lana KI\docs
C:\Carpuncle Cloud\Lana KI\gpt-gems
C:\Carpuncle Cloud\Lana KI\infra
C:\Carpuncle Cloud\Lana KI\Lana Git
C:\Carpuncle Cloud\Lana KI\logs
C:\Carpuncle Cloud\Lana KI\packages
C:\Carpuncle Cloud\Lana KI\runtime
C:\Carpuncle Cloud\Lana KI\scripts
C:\Carpuncle Cloud\Lana KI\security
C:\Carpuncle Cloud\Lana KI\Sync
C:\Carpuncle Cloud\Lana KI\Vault
Dot-Folder Policy
Dot-Folder gehoeren gebuendelt unter C:\Carpuncle Cloud\carpuncle.V6, soweit das jeweilige Tool technisch umleitbar ist. Dot-Folder sind ueberall entstanden, weil viele Tools standardmaessig in %USERPROFILE%, Projektordner oder den aktuellen Arbeitsordner schreiben. Das ist ein Konsolidierungsproblem, kein neuer RuntimeRoot.

Vorhandene zentrale Dot-Folder:

C:\Carpuncle Cloud\carpuncle.V6\.mg
C:\Carpuncle Cloud\carpuncle.V6\.nuget
C:\Carpuncle Cloud\carpuncle.V6\.openroute
C:\Carpuncle Cloud\carpuncle.V6\.pm2
C:\Carpuncle Cloud\carpuncle.V6\.slack
C:\Carpuncle Cloud\carpuncle.V6\.ssh
C:\Carpuncle Cloud\carpuncle.V6\.vscode
C:\Carpuncle Cloud\carpuncle.V6\.vscode-shared
C:\Carpuncle Cloud\carpuncle.V6\.agents
C:\Carpuncle Cloud\carpuncle.V6\.AIClient
C:\Carpuncle Cloud\carpuncle.V6\.android
C:\Carpuncle Cloud\carpuncle.V6\.antigravity
C:\Carpuncle Cloud\carpuncle.V6\.azure
C:\Carpuncle Cloud\carpuncle.V6\.box
C:\Carpuncle Cloud\carpuncle.V6\.bubblewrap
C:\Carpuncle Cloud\carpuncle.V6\.cache
C:\Carpuncle Cloud\carpuncle.V6\.codex
C:\Carpuncle Cloud\carpuncle.V6\.github
C:\Carpuncle Cloud\carpuncle.V6\.lmstudio
C:\Carpuncle Cloud\carpuncle.V6\.local
Regel: diese Ordner nur auditieren, sichern und gezielt umleiten. Nicht blind loeschen, nicht roh synchronisieren, keine Secrets ausgeben.

Aktive Dokumente
docs/AGENT_HANDOFF.md
docs/AGENT_POLICY.md
docs/BOX_NAS_WEBDAV_INTEGRATION.md
docs/EXECUTIVE_SUMMARY.md
docs/HANDOVER.md
docs/LANA_CORE_MEMORY.md
docs/LANA_ENV_KEY_INDEX.md
docs/LANA_MCP_GATEWAY_ALL_AI_ACCOUNTS_FLOW.puml
docs/LANA_PATH_POLICY.md
docs/LANA_REPOSITORY_POLICY.md
docs/LANA_SYSTEM_BASELINE.md
docs/Lana_Notitzbuch.md
docs/Lana_Notizbuch.md
docs/MASTER_PLAN.md
docs/mcp-chatgpt-connector.md
docs/notebooklm_inventory.csv
docs/PLAN.md
docs/PROGRESS.md
docs/SECRETS_POLICY.md
docs/STATUS.md
docs/SYNC_NOTE.md
docs/UNIFIED_CHATINFOS.md
docs/zip
Quellenklassifizierung
Bereinigte Master-Quellen:

docs/UNIFIED_CHATINFOS.md
docs/LANA_PATH_POLICY.md
docs/EXECUTIVE_SUMMARY.md
docs/LANA_SYSTEM_BASELINE.md
docs/SYNC_NOTE.md
AGENTS.md
docs/LANA_MCP_GATEWAY_ALL_AI_ACCOUNTS_FLOW.puml
Kontextquellen mit Secret-Risiko:

docs/LANA_CORE_MEMORY.md
docs/LANA_ENV_KEY_INDEX.md
docs/Lana_Notitzbuch.md
.env
PDFs, ZIPs, Vault, Logs und private Profile
Regel: Kontextquellen mit Secret-Risiko nur auf Existenz, Hash, Datum, Grobstatus und Sanitizing-Bedarf pruefen. Keine Rohinhalte in Chat, Git, SharePoint, Box oder Cloudflare spiegeln.

Externe Austauschquellen
OneDrive/SharePoint-nahe Quellen unter C:\Users\carpu\OneDrive\LanaStudio
OneDrive/SharePoint-nahe Quellen unter T:\carpuncle.V6\OneDrive - Carpuncle.ai\Lana_KI
Box-Sync-ZIPs unter C:\Users\carpu\OneDrive\LanaStudio\Box Sync
Box AI / lana-ki.boxnote: enthaelt gebuendelte Analyse aus frueheren Fehlversuchen. Status: Kontextquelle, nicht automatisch Wahrheit.
ZIPs: gelten als gebuendelte Fehler-, Log-, Export- und Kontextpakete. Sie duerfen nicht blind entpackt, committed oder synchronisiert werden.
Status: Austausch-/Doku-/Sync-Schicht, nicht RuntimeRoot.

Architektur-Baseline
Node A: Hetzner / Public Edge / Cloudflare Tunnel / Gateway / MCP-Routing / Control Plane
Node B: lokaler Windows Desktop / Primary Compute / LM Studio 127.0.0.1:1234 / ComfyUI 127.0.0.1:8188
Node C: RunPod / Burst GPU / On-Demand Heavy Jobs
Node D: Debian Laptop / Admin / Memory / Monitoring / Relay / 192.168.178.101
Node E: GCP / experimentelle temporaere Worker
NAS: FritzBox / Vault / Cold Storage / Backups / offline-first / nur VPN
VPN / FRITZ!Box Inventar
VPN-Ziel: FRITZ!Box
Host carpu: 192.168.178.201, FRITZ!Box-VPN-Einstellungen vorhanden. Zugangsdaten: nicht im Notizbuch speichern.
Host u585979: 192.168.178.202, FRITZ!Box-VPN-Einstellungen vorhanden. Zweck laut Box-AI-Kontext: Box.com oder Hetzner Storage Drive/WebDAV anbinden. Zugangsdaten: nicht im Notizbuch speichern.
Einordnung: VPN-/NAS-/Relay-Kontext, nicht oeffentliche Runtime.
Domain-Baseline
lana-ki.de: Frontend / Companion-App
gateway.lana-ki.de: Edge / MCP / Connector Plane
carpuncle.de: Backend / Core API
carpuncle.org: Background Sync / Workflows
carpuncle.eu: M365 / Identity / Mail
MCP / Gateway
ChatGPT Custom MCP verbindet sich nicht direkt mit lokalen Diensten.
Oeffentlicher Einstieg: Node A / Gateway.
MCP URL laut Doku: https://gateway.lana-ki.de/mcp
Fallback laut Doku: https://gateway.lana-ki.de/sse
Bearer-Token darf nur als Secret-Referenz existieren, z. B. op://....
Live-Status von Gateway, Tunnel und Endpunkten: Unbestaetigt.
Repository-Policy
Master laut lokaler Policy: github.com/carpu86/Lana
Doku-/Uebergangsquelle laut lokaler Policy: github.com/carpu86/Lana_Notitzbuch.md
Gesamtprojekt laut Baseline: carpu86/*, carpuapp/*, lana-ki-de/*
Jedes Repo muss MCP-Dateien enthalten.
GitHub darf lokal nur ueber C:\Carpuncle Cloud\Lana KI\Lana Git bearbeitet werden. Direkte GitHub-Schreibwege sind nicht die normale Arbeitsweise.
Lokaler MCP-Compliance-Stand: Unbestaetigt.
Ziel fuer SharePoint / Box / GitHub
SharePoint / OneDrive: Ziel wurde connector-seitig als carpu-my.sharepoint.com/personal/carpu_lana-ki_de mit Bibliothek Dokumente bestaetigt.
SharePoint-Ordner: Lana_Notizbuch.
Box.com: soll als Notizbuch-/Austauschquelle eingebunden werden. Kein aktiver Box-Connector in dieser Session belegt.
Box.com an FRITZ!Box: nicht direkt belegt. Pragmatischer Weg ist rclone/Box Drive auf Node B oder Node D und danach Sync/Mirror zum NAS.
Hetzner Storage/WebDAV: fuer NAS-nahe Dateiablage technisch naheliegender als Box.com, falls WebDAV/StorageBox-Zugang vorhanden ist. Secrets bleiben im Vault/1Password.
GitHub: soll bereinigte Doku/MCP-Policy aufnehmen, aber keine Secrets, Roh-ZIPs, Vaults oder Logs.
Cloudflare: soll Gateway/MCP/Connector Plane abbilden, aber keine Master-Secrets speichern.
Secret-Status
Im Verlauf und in lokalen Rohquellen wurden Klartext-Secrets gefunden bzw. offengelegt. Status: kompromittiert.

Aktueller Sanitizing-Befund: Die bereinigten Master-Zieldateien enthalten keine offensichtlichen Secret-Muster. LANA_CORE_MEMORY.md, LANA_ENV_KEY_INDEX.md und Lana_Notitzbuch.md enthalten Treffer in Secret-/Token-/Key-Mustern und bleiben deshalb sensible Kontextquellen.

Nicht ausgeben, nicht committen, nicht nach SharePoint/Box/GitHub spiegeln:

Passwoerter
API-Keys
OAuth-Secrets
private Schluessel
Tunnel-Tokens
Service-Account-Keys
.env
Vaults
Roh-ZIPs mit unbekanntem Inhalt
Logs mit Tokens oder Credentials
Empfehlung: vollstaendige Rotation und Umstellung auf 1Password/op-Referenzen.

Offene Punkte
SharePoint-Ziel wurde bestaetigt: carpu-my.sharepoint.com/personal/carpu_lana-ki_de, Bibliothek Dokumente, Ordner Lana_Notizbuch.
GitHub-Repos unter carpu86/*, carpuapp/*, lana-ki-de/* inventarisieren.
MCP-Dateien pro Repo pruefen und ergaenzen.
Cloudflare Gateway/Tunnel live pruefen.
Box.com-Anbindung klaeren.
Hetzner Storage/WebDAV gegen Box.com als NAS-Sync-Ziel entscheiden.
AGENTS.md - Lana-KI Review-Regeln
Stand: 2026-05-16

Projektkontext
Projekt: Carpuncle Cloud / Lana-KI
UserRoot / gebuendelte Toolprofile: C:\Carpuncle Cloud\carpuncle.V6
RuntimeRoot / aktiver Arbeitsordner: C:\Carpuncle Cloud\Lana KI
ToolRoot: C:\Carpuncle Cloud\Tools
DokuRoot: C:\Carpuncle Cloud\Lana KI\docs
Git-/Repo-Ledger und einzige erlaubte lokale GitHub-Arbeitsflaeche: C:\Carpuncle Cloud\Lana KI\Lana Git
Aktive .env: C:\Carpuncle Cloud\Lana KI\.env
GitHub- und Sync-Regel
GitHub-Arbeit lokal nur ueber C:\Carpuncle Cloud\Lana KI\Lana Git.
Keine GitHub-Arbeit aus OneDrive, Box Sync, SharePoint-Sync, ZIP-Exports, Desktop-Downloads oder fremden Arbeitsordnern.
Keine direkten GitHub-Connector-Schreibungen als Normalweg.
.env, Vaults, Roh-ZIPs und Logs mit Secrets duerfen nicht synchronisiert oder committed werden.
Archiv- und Sensibilitaetszonen
Diese Pfade sind nicht als produktiver Backend-Code zu bewerten:

docs\zip
archive-index
logs
Vault
Scans duerfen diese Bereiche inventarisieren. Treffer in diesen Bereichen sind nicht automatisch Code-Fails, sondern muessen als Archiv-/Analyse-/Secret-Risiko eingeordnet werden.

Dokumentationskonsolidierung
Primaere bereinigte Master-Doku: C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md.
Gueltige System-Baseline: C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md.
Die Root-Datei C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md ist leer und nicht als Quelle zu verwenden.
LANA_ENV_KEY_INDEX.md, Lana_Notitzbuch.md, PDFs, ZIPs, Vault, Logs und .env sind sensible Kontextquellen. Nur nach Sanitizing verwenden.
Dot-Folder-Regel
Dot-Folder gehoeren, soweit technisch moeglich, unter C:\Carpuncle Cloud\carpuncle.V6.
Dot-Folder nur auditieren, sichern und gezielt umleiten.
Keine Dot-Folder blind loeschen.
Inhalte sensibler Dot-Folder wie .ssh, .azure, .box, .codex, .github, .lmstudio, .pm2 nicht ausgeben.
MCP-Baseline
Transport: streamable-http
Tools: run_comfyui_workflow, ask_lmstudio, search_lana_memory, execute_shell_on_node
Absicherung: Bearer-Token ueber .env-Referenz MCP_BEARER_TOKEN_REF
Review guidelines
Sicherheit & Secrets (P0)
Keine Secrets, API-Keys, Tokens oder Passwoerter im Code; nur Env-Var-Namen als Referenzen im *_REF-Pattern.
Secrets grundsaetzlich nur ueber Settings.resolve_secret() aufloesen, niemals direkt per os.getenv() in Business-Logik.
Keine .env-Dateien im Repository; .env.example-Dateien ohne echte Werte sind erlaubt.
SSH-Keys, Cloudflare-Credentials und 1Password-Exporte duerfen nie ins Repo.
Authentifizierung & Autorisierung (P0)
Jede MCP-Route (/mcp) muss ueber hmac.compare_digest gegen das Bearer-Token abgesichert sein.
execute_shell_on_node darf nur ausgefuehrt werden, wenn settings.enable_shell_tools explizit True ist. Verstoesse dagegen sind P0.
Admin-Checks in Telegram-Befehlen muessen ueber is_admin() laufen, nie direkt verglichen.
Logging & PII (P1)
Keine print()-Aufrufe in Produktionscode; ausschliesslich logging.* verwenden.
Keine personenbezogenen Daten wie Nutzernamen, IDs oder Chat-Inhalte im Klartext in Logs.
Secrets duerfen niemals geloggt werden, auch nicht als Debug-Ausgabe.
ComfyUI-Constraints (P1)
Alle Workflows muessen lowvram=True erzwingen und Aufloesung auf maximal 512x512 begrenzen.
VAEDecode muss immer zu TiledVAEDecode umgeschrieben werden.
Direkte VAEDecode-Nutzung ist ein Review-Fehler.
HTTP & Timeouts (P1)
Jeder httpx.AsyncClient-Aufruf muss einen expliziten timeout-Parameter setzen.
Timeout-Wert kommt aus Settings.
Keine unbegrenzten HTTP-Calls ohne Timeout.
Konfiguration & Pfade (P1)
Keine Hardcoded-Pfade zu Legacy-Verzeichnissen wie LanaApp, Lana KI.env, 00_docs oder Lana KI\Tools.
Kanonische Root-Pfade kommen ausschliesslich aus Settings-Feldern.
TAILSCALE_NODES_JSON muss valides JSON sein.
Aenderungen an TAILSCALE_NODES_JSON muessen json.JSONDecodeError-Handling pruefen.
Code-Qualitaet (P2)
Neue oeffentliche Klassen/Funktionen in backend/ muessen Type-Annotations haben.
Async-Funktionen muessen await korrekt verwenden.
Blockierende Calls in Async-Code laufen via asyncio.to_thread.
Keine doppelten schedule-Tags beim AutonomousScheduler.
Vor neuer Registrierung schedule.clear("lana-autonomous") ausfuehren.
Tests (P2)
Neue Backend-Module muessen einen zugehoerigen Test in tests/ haben.

Lana-KI Unified Chatinfos
Stand: 2026-05-16

Zweck
Diese Datei ist der bereinigte zentrale Einstiegspunkt fuer Lana-KI / Carpuncle Cloud. Sie ersetzt keine Rohquellen, sondern fasst den aktuell belegten Projektstand secret-safe zusammen.

Konsolidierungsstand
Konsolidiert am: 2026-05-16
Primaere Quelle: C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md
Aktiver Doku-Ort: C:\Carpuncle Cloud\Lana KI\docs
Gueltige System-Baseline: C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md
Nicht als Quelle verwenden: C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md, weil die Root-Datei aktuell leer ist.
Visuelles Asset: C:\Carpuncle Cloud\Lana KI\docs\lana_logo_192x192.png; nur Logo/Branding, keine Architekturquelle.
Kanonische lokale Quellen
UserRoot / gebuendelte Toolprofile: C:\Carpuncle Cloud\carpuncle.V6
RuntimeRoot: C:\Carpuncle Cloud\Lana KI
ToolRoot: C:\Carpuncle Cloud\Tools
Aktive Doku: C:\Carpuncle Cloud\Lana KI\docs
Lokale Arbeitskopie in dieser Session: T:\Lana KI
Git-/Repo-Ledger und einzige erlaubte GitHub-Arbeitsflaeche: C:\Carpuncle Cloud\Lana KI\Lana Git
Runtime-Konfiguration im aktiven Workspace: C:\Carpuncle Cloud\Lana KI\.env
Hinweis: T:\Lana KI ist in dieser Session nur Spiegel/Arbeitsansicht, nicht neue Projektwahrheit.
Erlaubte RuntimeRoot-Unterordner
C:\Carpuncle Cloud\Lana KI\apps
C:\Carpuncle Cloud\Lana KI\archive-index
C:\Carpuncle Cloud\Lana KI\audit
C:\Carpuncle Cloud\Lana KI\cloudflare
C:\Carpuncle Cloud\Lana KI\config
C:\Carpuncle Cloud\Lana KI\docs
C:\Carpuncle Cloud\Lana KI\gpt-gems
C:\Carpuncle Cloud\Lana KI\infra
C:\Carpuncle Cloud\Lana KI\Lana Git
C:\Carpuncle Cloud\Lana KI\logs
C:\Carpuncle Cloud\Lana KI\packages
C:\Carpuncle Cloud\Lana KI\runtime
C:\Carpuncle Cloud\Lana KI\scripts
C:\Carpuncle Cloud\Lana KI\security
C:\Carpuncle Cloud\Lana KI\Sync
C:\Carpuncle Cloud\Lana KI\Vault
Dot-Folder Policy
Dot-Folder gehoeren gebuendelt unter C:\Carpuncle Cloud\carpuncle.V6, soweit das jeweilige Tool technisch umleitbar ist. Dot-Folder sind ueberall entstanden, weil viele Tools standardmaessig in %USERPROFILE%, Projektordner oder den aktuellen Arbeitsordner schreiben. Das ist ein Konsolidierungsproblem, kein neuer RuntimeRoot.

Vorhandene zentrale Dot-Folder:

C:\Carpuncle Cloud\carpuncle.V6\.mg
C:\Carpuncle Cloud\carpuncle.V6\.nuget
C:\Carpuncle Cloud\carpuncle.V6\.openroute
C:\Carpuncle Cloud\carpuncle.V6\.pm2
C:\Carpuncle Cloud\carpuncle.V6\.slack
C:\Carpuncle Cloud\carpuncle.V6\.ssh
C:\Carpuncle Cloud\carpuncle.V6\.vscode
C:\Carpuncle Cloud\carpuncle.V6\.vscode-shared
C:\Carpuncle Cloud\carpuncle.V6\.agents
C:\Carpuncle Cloud\carpuncle.V6\.AIClient
C:\Carpuncle Cloud\carpuncle.V6\.android
C:\Carpuncle Cloud\carpuncle.V6\.antigravity
C:\Carpuncle Cloud\carpuncle.V6\.azure
C:\Carpuncle Cloud\carpuncle.V6\.box
C:\Carpuncle Cloud\carpuncle.V6\.bubblewrap
C:\Carpuncle Cloud\carpuncle.V6\.cache
C:\Carpuncle Cloud\carpuncle.V6\.codex
C:\Carpuncle Cloud\carpuncle.V6\.github
C:\Carpuncle Cloud\carpuncle.V6\.lmstudio
C:\Carpuncle Cloud\carpuncle.V6\.local
Regel: diese Ordner nur auditieren, sichern und gezielt umleiten. Nicht blind loeschen, nicht roh synchronisieren, keine Secrets ausgeben.

Aktive Dokumente
docs/AGENT_HANDOFF.md
docs/AGENT_POLICY.md
docs/BOX_NAS_WEBDAV_INTEGRATION.md
docs/EXECUTIVE_SUMMARY.md
docs/HANDOVER.md
docs/LANA_CORE_MEMORY.md
docs/LANA_ENV_KEY_INDEX.md
docs/LANA_MCP_GATEWAY_ALL_AI_ACCOUNTS_FLOW.puml
docs/LANA_PATH_POLICY.md
docs/LANA_REPOSITORY_POLICY.md
docs/LANA_SYSTEM_BASELINE.md
docs/Lana_Notitzbuch.md
docs/Lana_Notizbuch.md
docs/MASTER_PLAN.md
docs/mcp-chatgpt-connector.md
docs/notebooklm_inventory.csv
docs/PLAN.md
docs/PROGRESS.md
docs/SECRETS_POLICY.md
docs/STATUS.md
docs/SYNC_NOTE.md
docs/UNIFIED_CHATINFOS.md
docs/zip
Quellenklassifizierung
Bereinigte Master-Quellen:

docs/UNIFIED_CHATINFOS.md
docs/LANA_PATH_POLICY.md
docs/EXECUTIVE_SUMMARY.md
docs/LANA_SYSTEM_BASELINE.md
docs/SYNC_NOTE.md
AGENTS.md
docs/LANA_MCP_GATEWAY_ALL_AI_ACCOUNTS_FLOW.puml
Kontextquellen mit Secret-Risiko:

docs/LANA_CORE_MEMORY.md
docs/LANA_ENV_KEY_INDEX.md
docs/Lana_Notitzbuch.md
.env
PDFs, ZIPs, Vault, Logs und private Profile
Regel: Kontextquellen mit Secret-Risiko nur auf Existenz, Hash, Datum, Grobstatus und Sanitizing-Bedarf pruefen. Keine Rohinhalte in Chat, Git, SharePoint, Box oder Cloudflare spiegeln.

Externe Austauschquellen
OneDrive/SharePoint-nahe Quellen unter C:\Users\carpu\OneDrive\LanaStudio
OneDrive/SharePoint-nahe Quellen unter T:\carpuncle.V6\OneDrive - Carpuncle.ai\Lana_KI
Box-Sync-ZIPs unter C:\Users\carpu\OneDrive\LanaStudio\Box Sync
Box AI / lana-ki.boxnote: enthaelt gebuendelte Analyse aus frueheren Fehlversuchen. Status: Kontextquelle, nicht automatisch Wahrheit.
ZIPs: gelten als gebuendelte Fehler-, Log-, Export- und Kontextpakete. Sie duerfen nicht blind entpackt, committed oder synchronisiert werden.
Status: Austausch-/Doku-/Sync-Schicht, nicht RuntimeRoot.

Architektur-Baseline
Node A: Hetzner / Public Edge / Cloudflare Tunnel / Gateway / MCP-Routing / Control Plane
Node B: lokaler Windows Desktop / Primary Compute / LM Studio 127.0.0.1:1234 / ComfyUI 127.0.0.1:8188
Node C: RunPod / Burst GPU / On-Demand Heavy Jobs
Node D: Debian Laptop / Admin / Memory / Monitoring / Relay / 192.168.178.101
Node E: GCP / experimentelle temporaere Worker
NAS: FritzBox / Vault / Cold Storage / Backups / offline-first / nur VPN
VPN / FRITZ!Box Inventar
VPN-Ziel: FRITZ!Box
Host carpu: 192.168.178.201, FRITZ!Box-VPN-Einstellungen vorhanden. Zugangsdaten: nicht im Notizbuch speichern.
Host u585979: 192.168.178.202, FRITZ!Box-VPN-Einstellungen vorhanden. Zweck laut Box-AI-Kontext: Box.com oder Hetzner Storage Drive/WebDAV anbinden. Zugangsdaten: nicht im Notizbuch speichern.
Einordnung: VPN-/NAS-/Relay-Kontext, nicht oeffentliche Runtime.
Domain-Baseline
lana-ki.de: Frontend / Companion-App
gateway.lana-ki.de: Edge / MCP / Connector Plane
carpuncle.de: Backend / Core API
carpuncle.org: Background Sync / Workflows
carpuncle.eu: M365 / Identity / Mail
MCP / Gateway
ChatGPT Custom MCP verbindet sich nicht direkt mit lokalen Diensten.
Oeffentlicher Einstieg: Node A / Gateway.
MCP URL laut Doku: https://gateway.lana-ki.de/mcp
Fallback laut Doku: https://gateway.lana-ki.de/sse
Bearer-Token darf nur als Secret-Referenz existieren, z. B. op://....
Live-Status von Gateway, Tunnel und Endpunkten: Unbestaetigt.
Repository-Policy
Master laut lokaler Policy: github.com/carpu86/Lana
Doku-/Uebergangsquelle laut lokaler Policy: github.com/carpu86/Lana_Notitzbuch.md
Gesamtprojekt laut Baseline: carpu86/*, carpuapp/*, lana-ki-de/*
Jedes Repo muss MCP-Dateien enthalten.
GitHub darf lokal nur ueber C:\Carpuncle Cloud\Lana KI\Lana Git bearbeitet werden. Direkte GitHub-Schreibwege sind nicht die normale Arbeitsweise.
Lokaler MCP-Compliance-Stand: Unbestaetigt.
Ziel fuer SharePoint / Box / GitHub
SharePoint / OneDrive: Ziel wurde connector-seitig als carpu-my.sharepoint.com/personal/carpu_lana-ki_de mit Bibliothek Dokumente bestaetigt.
SharePoint-Ordner: Lana_Notizbuch.
Box.com: soll als Notizbuch-/Austauschquelle eingebunden werden. Kein aktiver Box-Connector in dieser Session belegt.
Box.com an FRITZ!Box: nicht direkt belegt. Pragmatischer Weg ist rclone/Box Drive auf Node B oder Node D und danach Sync/Mirror zum NAS.
Hetzner Storage/WebDAV: fuer NAS-nahe Dateiablage technisch naheliegender als Box.com, falls WebDAV/StorageBox-Zugang vorhanden ist. Secrets bleiben im Vault/1Password.
GitHub: soll bereinigte Doku/MCP-Policy aufnehmen, aber keine Secrets, Roh-ZIPs, Vaults oder Logs.
Cloudflare: soll Gateway/MCP/Connector Plane abbilden, aber keine Master-Secrets speichern.
Secret-Status
Im Verlauf und in lokalen Rohquellen wurden Klartext-Secrets gefunden bzw. offengelegt. Status: kompromittiert.

Aktueller Sanitizing-Befund: Die bereinigten Master-Zieldateien enthalten keine offensichtlichen Secret-Muster. LANA_CORE_MEMORY.md, LANA_ENV_KEY_INDEX.md und Lana_Notitzbuch.md enthalten Treffer in Secret-/Token-/Key-Mustern und bleiben deshalb sensible Kontextquellen.

Nicht ausgeben, nicht committen, nicht nach SharePoint/Box/GitHub spiegeln:

Passwoerter
API-Keys
OAuth-Secrets
private Schluessel
Tunnel-Tokens
Service-Account-Keys
.env
Vaults
Roh-ZIPs mit unbekanntem Inhalt
Logs mit Tokens oder Credentials
Empfehlung: vollstaendige Rotation und Umstellung auf 1Password/op-Referenzen.

Offene Punkte
SharePoint-Ziel wurde bestaetigt: carpu-my.sharepoint.com/personal/carpu_lana-ki_de, Bibliothek Dokumente, Ordner Lana_Notizbuch.
GitHub-Repos unter carpu86/*, carpuapp/*, lana-ki-de/* inventarisieren.
MCP-Dateien pro Repo pruefen und ergaenzen.
Cloudflare Gateway/Tunnel live pruefen.
Box.com-Anbindung klaeren.
Hetzner Storage/WebDAV gegen Box.com als NAS-Sync-Ziel entscheiden.

LANA_SYSTEM_BASELINE
Stand: 2026-05-16

Projekt
Name: Carpuncle Cloud / Lana-KI
Hauptsystem: Windows
Shell: PowerShell 7
RuntimeRoot: C:\Carpuncle Cloud\Lana KI
DokuRoot: C:\Carpuncle Cloud\Lana KI\docs
UserRoot: C:\Carpuncle Cloud\carpuncle.V6
ToolRoot: C:\Carpuncle Cloud\Tools
GitHub lokal nur ueber: C:\Carpuncle Cloud\Lana KI\Lana Git
Aktive .env: C:\Carpuncle Cloud\Lana KI\.env
Domains
lana-ki.de: Frontend / Companion-App
gateway.lana-ki.de: Edge / MCP / Connector Plane
carpuncle.de: Backend / Core API
carpuncle.org: Background Sync / Workflows
carpuncle.eu: M365 / Identity / Mail
Nodes
Node A: Hetzner / Public Edge / Cloudflare Tunnel / Gateway / MCP-Routing / Control Plane
Node B: lokaler Windows Desktop / Primary Compute / LM Studio 127.0.0.1:1234 / ComfyUI 127.0.0.1:8188
Node C: RunPod / Burst GPU / On-Demand Heavy Jobs
Node D: Debian Laptop / Admin / Memory / Monitoring / Relay / 192.168.178.101
Node E: GCP / experimentelle temporaere Worker
NAS: FritzBox / Vault / Cold Storage / Backups / offline-first / nur VPN
MCP / Gateway
ChatGPT Custom MCP verbindet sich nicht direkt mit lokalen Diensten.
Oeffentlicher Einstieg: Node A / Gateway.
MCP URL laut Doku: https://gateway.lana-ki.de/mcp
Fallback laut Doku: https://gateway.lana-ki.de/sse
Bearer-Token nur als Secret-Referenz, nicht im Klartext.
Live-Status von Gateway, Tunnel und Endpunkten: unbestaetigt bis Healthcheck.
Quellenstatus
Diese Datei unter docs ist die gueltige System-Baseline.
Die Root-Datei C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md ist leer und nicht als Quelle zu verwenden.
Aeltere P0-Befunde aus importierten Dokumenten bleiben Kontext, bis sie live neu geprueft wurden.
Standard-Diagnose
Test-Path
Get-ChildItem
Get-NetTCPConnection
Get-CimInstance Win32_Process
Get-Content -Tail
Invoke-RestMethod
curl.exe
git status --short nur unter C:\Carpuncle Cloud\Lana KI\Lana Git
Verboten
Secret-Werte ausgeben
.env loeschen, leeren oder blind ueberschreiben
Cloudflare/CAPTCHA/Auth umgehen
P0 rot als Erfolg melden
Lana Sync Note
Stand: 2026-05-16

Root Cause
Chat-, Box-AI-, OneDrive-, SharePoint-, GitHub- und ZIP-Quellen waren verteilt. Zusaetzlich haben Tools Dot-Folder an mehreren Stellen erzeugt, weil viele Programme ohne zentrale HOME-/Profilumleitung in %USERPROFILE%, Projektordner oder den aktuellen Arbeitsordner schreiben.

Fix
Einheitliche lokale Wahrheit:

C:\Carpuncle Cloud\carpuncle.V6
C:\Carpuncle Cloud\Lana KI
C:\Carpuncle Cloud\Tools
GitHub-Arbeit nur ueber:

C:\Carpuncle Cloud\Lana KI\Lana Git
Aktive Doku:

C:\Carpuncle Cloud\Lana KI\docs
C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md
Dot-Folder werden unter C:\Carpuncle Cloud\carpuncle.V6 gebuendelt, soweit technisch moeglich. Keine Dot-Folder blind loeschen.

Konsolidierte Quellenregel
Primaere Master-Doku: C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md
Gueltige System-Baseline: C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md
Root-Datei C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md ist leer und keine Quelle.
LANA_ENV_KEY_INDEX.md, Lana_Notitzbuch.md, PDFs, ZIPs, Vault, Logs und .env sind sensible Kontextquellen und duerfen nicht roh synchronisiert werden.
Testblock
Vor Sync oder GitHub-Aktion:

Test-Path auf die drei Root-Pfade.
Secret-Scan auf Zielartefakte.
GitHub-Pfad muss C:\Carpuncle Cloud\Lana KI\Lana Git sein.

AGENTS.md - Lana-KI Review-Regeln
Stand: 2026-05-16

Projektkontext
Projekt: Carpuncle Cloud / Lana-KI
UserRoot / gebuendelte Toolprofile: C:\Carpuncle Cloud\carpuncle.V6
RuntimeRoot / aktiver Arbeitsordner: C:\Carpuncle Cloud\Lana KI
ToolRoot: C:\Carpuncle Cloud\Tools
DokuRoot: C:\Carpuncle Cloud\Lana KI\docs
Git-/Repo-Ledger und einzige erlaubte lokale GitHub-Arbeitsflaeche: C:\Carpuncle Cloud\Lana KI\Lana Git
Aktive .env: C:\Carpuncle Cloud\Lana KI\.env
GitHub- und Sync-Regel
GitHub-Arbeit lokal nur ueber C:\Carpuncle Cloud\Lana KI\Lana Git.
Keine GitHub-Arbeit aus OneDrive, Box Sync, SharePoint-Sync, ZIP-Exports, Desktop-Downloads oder fremden Arbeitsordnern.
Keine direkten GitHub-Connector-Schreibungen als Normalweg.
.env, Vaults, Roh-ZIPs und Logs mit Secrets duerfen nicht synchronisiert oder committed werden.
Archiv- und Sensibilitaetszonen
Diese Pfade sind nicht als produktiver Backend-Code zu bewerten:

docs\zip
archive-index
logs
Vault
Scans duerfen diese Bereiche inventarisieren. Treffer in diesen Bereichen sind nicht automatisch Code-Fails, sondern muessen als Archiv-/Analyse-/Secret-Risiko eingeordnet werden.

Dokumentationskonsolidierung
Primaere bereinigte Master-Doku: C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md.
Gueltige System-Baseline: C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md.
Die Root-Datei C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md ist leer und nicht als Quelle zu verwenden.
LANA_ENV_KEY_INDEX.md, Lana_Notitzbuch.md, PDFs, ZIPs, Vault, Logs und .env sind sensible Kontextquellen. Nur nach Sanitizing verwenden.
Dot-Folder-Regel
Dot-Folder gehoeren, soweit technisch moeglich, unter C:\Carpuncle Cloud\carpuncle.V6.
Dot-Folder nur auditieren, sichern und gezielt umleiten.
Keine Dot-Folder blind loeschen.
Inhalte sensibler Dot-Folder wie .ssh, .azure, .box, .codex, .github, .lmstudio, .pm2 nicht ausgeben.
MCP-Baseline
Transport: streamable-http
Tools: run_comfyui_workflow, ask_lmstudio, search_lana_memory, execute_shell_on_node
Absicherung: Bearer-Token ueber .env-Referenz MCP_BEARER_TOKEN_REF
Review guidelines
Sicherheit & Secrets (P0)
Keine Secrets, API-Keys, Tokens oder Passwoerter im Code; nur Env-Var-Namen als Referenzen im *_REF-Pattern.
Secrets grundsaetzlich nur ueber Settings.resolve_secret() aufloesen, niemals direkt per os.getenv() in Business-Logik.
Keine .env-Dateien im Repository; .env.example-Dateien ohne echte Werte sind erlaubt.
SSH-Keys, Cloudflare-Credentials und 1Password-Exporte duerfen nie ins Repo.
Authentifizierung & Autorisierung (P0)
Jede MCP-Route (/mcp) muss ueber hmac.compare_digest gegen das Bearer-Token abgesichert sein.
execute_shell_on_node darf nur ausgefuehrt werden, wenn settings.enable_shell_tools explizit True ist. Verstoesse dagegen sind P0.
Admin-Checks in Telegram-Befehlen muessen ueber is_admin() laufen, nie direkt verglichen.
Logging & PII (P1)
Keine print()-Aufrufe in Produktionscode; ausschliesslich logging.* verwenden.
Keine personenbezogenen Daten wie Nutzernamen, IDs oder Chat-Inhalte im Klartext in Logs.
Secrets duerfen niemals geloggt werden, auch nicht als Debug-Ausgabe.
ComfyUI-Constraints (P1)
Alle Workflows muessen lowvram=True erzwingen und Aufloesung auf maximal 512x512 begrenzen.
VAEDecode muss immer zu TiledVAEDecode umgeschrieben werden.
Direkte VAEDecode-Nutzung ist ein Review-Fehler.
HTTP & Timeouts (P1)
Jeder httpx.AsyncClient-Aufruf muss einen expliziten timeout-Parameter setzen.
Timeout-Wert kommt aus Settings.
Keine unbegrenzten HTTP-Calls ohne Timeout.
Konfiguration & Pfade (P1)
Keine Hardcoded-Pfade zu Legacy-Verzeichnissen wie LanaApp, Lana KI.env, 00_docs oder Lana KI\Tools.
Kanonische Root-Pfade kommen ausschliesslich aus Settings-Feldern.
TAILSCALE_NODES_JSON muss valides JSON sein.
Aenderungen an TAILSCALE_NODES_JSON muessen json.JSONDecodeError-Handling pruefen.
Code-Qualitaet (P2)
Neue oeffentliche Klassen/Funktionen in backend/ muessen Type-Annotations haben.
Async-Funktionen muessen await korrekt verwenden.
Blockierende Calls in Async-Code laufen via asyncio.to_thread.
Keine doppelten schedule-Tags beim AutonomousScheduler.
Vor neuer Registrierung schedule.clear("lana-autonomous") ausfuehren.
Tests (P2)
Neue Backend-Module muessen einen zugehoerigen Test in tests/ haben.

AGENTS.md - Lana-KI Review-Regeln
Stand: 2026-05-16

Projektkontext
Projekt: Carpuncle Cloud / Lana-KI
UserRoot / gebuendelte Toolprofile: C:\Carpuncle Cloud\carpuncle.V6
RuntimeRoot / aktiver Arbeitsordner: C:\Carpuncle Cloud\Lana KI
ToolRoot: C:\Carpuncle Cloud\Tools
DokuRoot: C:\Carpuncle Cloud\Lana KI\docs
Git-/Repo-Ledger und einzige erlaubte lokale GitHub-Arbeitsflaeche: C:\Carpuncle Cloud\Lana KI\Lana Git
Aktive .env: C:\Carpuncle Cloud\Lana KI\.env
GitHub- und Sync-Regel
GitHub-Arbeit lokal nur ueber C:\Carpuncle Cloud\Lana KI\Lana Git.
Keine GitHub-Arbeit aus OneDrive, Box Sync, SharePoint-Sync, ZIP-Exports, Desktop-Downloads oder fremden Arbeitsordnern.
Keine direkten GitHub-Connector-Schreibungen als Normalweg.
.env, Vaults, Roh-ZIPs und Logs mit Secrets duerfen nicht synchronisiert oder committed werden.
Archiv- und Sensibilitaetszonen
Diese Pfade sind nicht als produktiver Backend-Code zu bewerten:

docs\zip
archive-index
logs
Vault
Scans duerfen diese Bereiche inventarisieren. Treffer in diesen Bereichen sind nicht automatisch Code-Fails, sondern muessen als Archiv-/Analyse-/Secret-Risiko eingeordnet werden.

Dokumentationskonsolidierung
Primaere bereinigte Master-Doku: C:\Carpuncle Cloud\Lana KI\docs\UNIFIED_CHATINFOS.md.
Gueltige System-Baseline: C:\Carpuncle Cloud\Lana KI\docs\LANA_SYSTEM_BASELINE.md.
Die Root-Datei C:\Carpuncle Cloud\Lana KI\LANA_SYSTEM_BASELINE.md ist leer und nicht als Quelle zu verwenden.
LANA_ENV_KEY_INDEX.md, Lana_Notitzbuch.md, PDFs, ZIPs, Vault, Logs und .env sind sensible Kontextquellen. Nur nach Sanitizing verwenden.
Dot-Folder-Regel
Dot-Folder gehoeren, soweit technisch moeglich, unter C:\Carpuncle Cloud\carpuncle.V6.
Dot-Folder nur auditieren, sichern und gezielt umleiten.
Keine Dot-Folder blind loeschen.
Inhalte sensibler Dot-Folder wie .ssh, .azure, .box, .codex, .github, .lmstudio, .pm2 nicht ausgeben.
MCP-Baseline
Transport: streamable-http
Tools: run_comfyui_workflow, ask_lmstudio, search_lana_memory, execute_shell_on_node
Absicherung: Bearer-Token ueber .env-Referenz MCP_BEARER_TOKEN_REF
Review guidelines
Sicherheit & Secrets (P0)
Keine Secrets, API-Keys, Tokens oder Passwoerter im Code; nur Env-Var-Namen als Referenzen im *_REF-Pattern.
Secrets grundsaetzlich nur ueber Settings.resolve_secret() aufloesen, niemals direkt per os.getenv() in Business-Logik.
Keine .env-Dateien im Repository; .env.example-Dateien ohne echte Werte sind erlaubt.
SSH-Keys, Cloudflare-Credentials und 1Password-Exporte duerfen nie ins Repo.
Authentifizierung & Autorisierung (P0)
Jede MCP-Route (/mcp) muss ueber hmac.compare_digest gegen das Bearer-Token abgesichert sein.
execute_shell_on_node darf nur ausgefuehrt werden, wenn settings.enable_shell_tools explizit True ist. Verstoesse dagegen sind P0.
Admin-Checks in Telegram-Befehlen muessen ueber is_admin() laufen, nie direkt verglichen.
Logging & PII (P1)
Keine print()-Aufrufe in Produktionscode; ausschliesslich logging.* verwenden.
Keine personenbezogenen Daten wie Nutzernamen, IDs oder Chat-Inhalte im Klartext in Logs.
Secrets duerfen niemals geloggt werden, auch nicht als Debug-Ausgabe.
ComfyUI-Constraints (P1)
Alle Workflows muessen lowvram=True erzwingen und Aufloesung auf maximal 512x512 begrenzen.
VAEDecode muss immer zu TiledVAEDecode umgeschrieben werden.
Direkte VAEDecode-Nutzung ist ein Review-Fehler.
HTTP & Timeouts (P1)
Jeder httpx.AsyncClient-Aufruf muss einen expliziten timeout-Parameter setzen.
Timeout-Wert kommt aus Settings.
Keine unbegrenzten HTTP-Calls ohne Timeout.
Konfiguration & Pfade (P1)
Keine Hardcoded-Pfade zu Legacy-Verzeichnissen wie LanaApp, Lana KI.env, 00_docs oder Lana KI\Tools.
Kanonische Root-Pfade kommen ausschliesslich aus Settings-Feldern.
TAILSCALE_NODES_JSON muss valides JSON sein.
Aenderungen an TAILSCALE_NODES_JSON muessen json.JSONDecodeError-Handling pruefen.
Code-Qualitaet (P2)
Neue oeffentliche Klassen/Funktionen in backend/ muessen Type-Annotations haben.
Async-Funktionen muessen await korrekt verwenden.
Blockierende Calls in Async-Code laufen via asyncio.to_thread.
Keine doppelten schedule-Tags beim AutonomousScheduler.
Vor neuer Registrierung schedule.clear("lana-autonomous") ausfuehren.
Tests (P2)
Neue Backend-Module muessen einen zugehoerigen Test in tests/ haben.



- Endpoint: `https://gateway.lana-ki.de/mcp`
- Transport: `streamable-http`
- Tools: `run_comfyui_workflow`, `ask_lmstudio`, `search_lana_memory`, `execute_shell_on_node`
- Absicherung: Bearer-Token über `.env`-Referenz `MCP_BEARER_TOKEN_REF`
