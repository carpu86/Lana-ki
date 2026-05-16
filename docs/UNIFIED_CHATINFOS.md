# Lana-KI Unified Chatinfos

Stand: 2026-05-16

## Zweck

Diese Datei ist der bereinigte zentrale Einstiegspunkt fuer Lana-KI / Carpuncle Cloud. Sie ersetzt keine Rohquellen, sondern fasst den aktuell belegten Projektstand secret-safe zusammen.

## Kanonische lokale Quellen

- RuntimeRoot: `C:\Carpuncle Cloud\Lana KI`
- Aktive Doku: `C:\Carpuncle Cloud\Lana KI\docs`
- Lokale Arbeitskopie in dieser Session: `T:\Lana KI`
- Git-/Repo-Ledger: `C:\Carpuncle Cloud\Lana KI\Lana Git`
- ToolRoot: `C:\Carpuncle Cloud\Tools`
- UserRoot: `C:\Carpuncle Cloud\carpuncle.V6`
- Runtime-Konfiguration lokal belegt: `C:\Carpuncle Cloud\.env`
- Vorgabe-Konflikt: `C:\Carpuncle Cloud.env` ist in der aktuellen lokalen Pruefung nicht belegt.

## Aktive Dokumente

- `docs/EXECUTIVE_SUMMARY.md`
- `docs/LANA_CORE_MEMORY.md`
- `docs/LANA_PATH_POLICY.md`
- `docs/LANA_SYSTEM_BASELINE.md`
- `docs/Lana_Notitzbuch.md`
- `docs/Lana_Notizbuch.md`
- `docs/MASTER_PLAN.md`
- `docs/mcp-chatgpt-connector.md`
- `docs/LANA_REPOSITORY_POLICY.md`
- `docs/LANA_ENV_KEY_INDEX.md`

## Externe Austauschquellen

- OneDrive/SharePoint-nahe Quellen unter `C:\Users\carpu\OneDrive\LanaStudio`
- OneDrive/SharePoint-nahe Quellen unter `T:\carpuncle.V6\OneDrive - Carpuncle.ai\Lana_KI`
- Box-Sync-ZIPs unter `C:\Users\carpu\OneDrive\LanaStudio\Box Sync`

Status: Austausch-/Doku-/Sync-Schicht, nicht RuntimeRoot.

## Architektur-Baseline

- Node A: Hetzner / Public Edge / Cloudflare Tunnel / Gateway / MCP-Routing / Control Plane
- Node B: lokaler Windows Desktop / Primary Compute / LM Studio `127.0.0.1:1234` / ComfyUI `127.0.0.1:8188`
- Node C: RunPod / Burst GPU / On-Demand Heavy Jobs
- Node D: Debian Laptop / Admin / Memory / Monitoring / Relay / `192.168.178.101`
- Node E: GCP / experimentelle temporaere Worker
- NAS: FritzBox / Vault / Cold Storage / Backups / offline-first / nur VPN

## Domain-Baseline

- `lana-ki.de`: Frontend / Companion-App
- `gateway.lana-ki.de`: Edge / MCP / Connector Plane
- `carpuncle.de`: Backend / Core API
- `carpuncle.org`: Background Sync / Workflows
- `carpuncle.eu`: M365 / Identity / Mail

## MCP / Gateway

- ChatGPT Custom MCP verbindet sich nicht direkt mit lokalen Diensten.
- Oeffentlicher Einstieg: Node A / Gateway.
- MCP URL laut Doku: `https://gateway.lana-ki.de/mcp`
- Fallback laut Doku: `https://gateway.lana-ki.de/sse`
- Bearer-Token darf nur als Secret-Referenz existieren, z. B. `op://...`.
- Live-Status von Gateway, Tunnel und Endpunkten: Unbestaetigt.

## Repository-Policy

- Master laut lokaler Policy: `github.com/carpu86/Lana`
- Doku-/Uebergangsquelle laut lokaler Policy: `github.com/carpu86/Lana_Notitzbuch.md`
- Gesamtprojekt laut Baseline: `carpu86/*`, `carpuapp/*`, `lana-ki-de/*`
- Jedes Repo muss MCP-Dateien enthalten.
- Lokaler MCP-Compliance-Stand: Unbestaetigt.

## Ziel fuer SharePoint / Box / GitHub

- SharePoint `carpu.onmicrosoft.com`: soll Lanas bereinigtes Notizbuch / Doku-Portal werden. Zielsite und Bibliothek sind noch nicht bestaetigt.
- Box.com: soll als Notizbuch-/Austauschquelle eingebunden werden. Kein aktiver Box-Connector in dieser Session belegt.
- GitHub: soll bereinigte Doku/MCP-Policy aufnehmen, aber keine Secrets, Roh-ZIPs, Vaults oder Logs.
- Cloudflare: soll Gateway/MCP/Connector Plane abbilden, aber keine Master-Secrets speichern.

## Secret-Status

Im Verlauf und in lokalen Rohquellen wurden Klartext-Secrets gefunden bzw. offengelegt. Status: kompromittiert.

Nicht ausgeben, nicht committen, nicht nach SharePoint/Box/GitHub spiegeln:

- Passwoerter
- API-Keys
- OAuth-Secrets
- private Schluessel
- Tunnel-Tokens
- Service-Account-Keys
- `.env`
- Vaults
- Roh-ZIPs mit unbekanntem Inhalt
- Logs mit Tokens oder Credentials

Empfehlung: vollstaendige Rotation und Umstellung auf 1Password/op-Referenzen.

## Offene Punkte

- SharePoint Hostname/Site/Bibliothek bestaetigen.
- GitHub-Repos unter `carpu86/*`, `carpuapp/*`, `lana-ki-de/*` inventarisieren.
- MCP-Dateien pro Repo pruefen und ergaenzen.
- Cloudflare Gateway/Tunnel live pruefen.
- Box.com-Anbindung klaeren.
- Rohquellen sanitizen, hashen und nur bereinigt uebernehmen.
