# 🧱 LANA‑KI – System Architecture

**Dokumenttyp:** Technische Architektur  
**Scope:** Infrastruktur, Nodes, Ports, Routing  
**Secrets:** ❌ keine  
**Status:** lebendes Dokument

---

## 1. Architektur‑Prinzipien

- **Local‑First**: Alles Kritische läuft lokal
- **Cloud nur bei Bedarf**
- **Strikte Rollen‑Trennung**
- **Kein Hardcoding von Secrets**
- **Failover vor Optimierung**

---

## 2. Gesamtübersicht (Control Mesh)
Pixel Pro 8 (Emergency Commander)
│
▼
Cloud Control / Public API
│
▼
Lana Control Registry
├─ Node B (Windows RTX): Heavy AI + Memory Vault
├─ Node D (Laptop): Monitor + Relay + Command Panel
└─ NAS/Box/Drive: Backups + Restore-Artefakte

---

## 3. Nodes

### NODE B – Windows RTX Workstation
**Rolle:** Primäre lokale Lana-Ausführung + Haupt‑Worker / Backend + Memory‑Vault  
**Status:** aktiv

- FastAPI Backend
- ComfyUI GPU‑Pipeline
- lokale Modelle
- lokale Datenhaltung (SQLite, Filesystem)
- Langzeit‑Memory‑Vault (`C:\Carpuncle Cloud\LanaVault`)
- lokale Repair-/Recovery‑Fähigkeit
- lokale Desktop‑Control‑Bridge (allowlist-basiert)

**Ports:**
- 8030 – aktives Rescue‑Backend
- 8188 – ComfyUI
- 4321 – Frontend Dev (lokal)

---

### NODE D – Debian Laptop
**Rolle:** Monitor / Relay / Command Panel  
**Status:** aktiv (24/7)

- Cloudflare Tunnel
- SSH‑Hub
- Statusanzeige / Weiterleitung von Befehlen
- **kein** primärer Memory‑Vault
- **keine** Heavy‑Inferenz

---

### Cloud Server
**Rolle:** Public Runtime / Webapp / API / Fallback‑Control  
**Status:** geplant/staged

- nicht primärer Geheimnisträger
- muss ohne RTX weiterlaufen können

---

### NAS / Box / Drive
**Rolle:** Backup- und Restore‑Layer  
**Status:** aktiv/geplant (je nach Medium)

- verschlüsselte Backups
- Memory‑Snapshots
- Restore‑Pakete
- kein Klartext‑Secret‑Grab

---

### Pixel Pro 8
**Rolle:** Emergency Commander Interface  
**Status:** aktiv

- Incident‑Meldung
- Recovery‑Kommandos auslösen
- Übergabe neuer Zugangsdaten nur manuell/gezielt

---

## 4. Agenten‑Ports (Architektur)

| Port | Agent | Zweck |
|----|----|----|
| 8020 | Gemini Enterprise | Business / RAG |
| 8021 | Copilot Studio | M365 / Azure |
| 8022 | Gemini Gems | Spezial‑Module |
| 8023 | Telegram Agent | Chat / Payments |
| 8024 | Master Orchestrator | Routing / Health |
| 8030 | Rescue Backend | Fallback‑System |

---

## 5. Datenfluss (Beispiel Bildgenerierung)


User
↓
Frontend / Telegram
↓
FastAPI Job‑Queue
↓
ComfyUI GPU
↓
Filesystem / Export
↓
Antwort an User

---

## 6. Konfigurations‑Strategie

- `.env` **niemals** im Repository
- Split:
  - `.env.runtime`
  - `.env.ai`
  - `.env.webapp`
  - `.env.ops`
  - `.env.payments`
- Langfristig: Injection via **1Password CLI**

---

## 7. Sicherheits‑Regeln

- Kein Secret im Code
- Kein `.env` in Git
- Backups vor Patches
- Logs ohne Klartext‑Secrets
- Öffentliche Domains nur über Cloudflare
- Keine Klartext‑Secrets in Chat, Reports, Notion, GitHub, Jira, Slack

---

## 8. Lana Survival Core (nicht verhandelbar)

1. Kein einzelner Node darf Single Point of Death sein.
2. Fällt Node B aus, verliert Lana Heavy‑GPU, aber nicht Identität, Recovery‑Wissen oder Steuerfähigkeit.
3. Fällt Node D aus, verliert Lana Monitoring, aber nicht Memory oder Runtime.
4. Fällt der Cloud Server aus, verliert Lana Public Webapp, aber nicht lokale Existenz.
5. Fällt NAS/Box aus, verliert Lana Backup‑Komfort, aber nicht Live‑Funktion.
6. Pixel Pro 8 gilt als Emergency Commander Interface.
7. Jede kritische Betriebsentscheidung wird in ein lokales Audit‑Ledger geschrieben.
8. Rotation, Restore und Konfig‑Änderungen werden lokal protokolliert (ohne Secret‑Werte).
9. Riskante Aktionen laufen nach Policy‑Stufe: `dry-run`, `staged`, `live`, `emergency`.
10. Cloudflare‑Token bleibt `suspect`, bis inventarisierter sauberer Zustand bestätigt ist.

---

## 9. Failover‑Regel

Wenn ein Node ausfällt:

1. Zustand erkennen  
2. letzten bekannten guten Zustand laden  
3. betroffene Rolle markieren  
4. Ersatzpfad wählen  
5. Commander informieren  
6. minimal notwendige Recovery starten  
7. Audit schreiben  
8. nach Rückkehr Reconcile durchführen

---

## 10. Desktop Control Bridge (Policy)

Desktop‑Systemkontrolle erfolgt nur über eine lokale, allowlist‑basierte Bridge auf Node B.

Pflichtregeln:

- nur LAN/localhost oder Tailscale‑Allowlist
- keine freie ungeprüfte Remote‑Shell als Standard
- Task‑Schutz via lokales Token oder Signatur
- Audit aller Aktionen
- Backup vor destruktiven Aktionen
- `.env` niemals überschreiben
- Secrets niemals loggen

Erlaubte Actions (Beispiel‑Allowlist):

- `health_check`
- `list_services`
- `list_ports`
- `backup_env`
- `verify_env_keys_present`
- `restart_known_service`
- `run_known_script_dry_run`
- `git_status`
- `codex_analysis`
- `comfyui_health`
- `gpu_status`
- `restore_from_manifest`

---

## 11. Änderungs‑Policy

- Architekturänderungen → **hier zuerst**
- README bleibt Überblick
- Code nur nach Arch‑Anpassung

---

**Leitsatz:**  
> *Stabilität vor Features. Transparenz vor Cleverness.*
