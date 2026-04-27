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

## 2. Gesamtübersicht
Internet
│
▼
Cloudflare DNS
│
▼
Cloudflare Tunnel (NODE D)
│
▼
Windows Backend (NODE B)
├─ FastAPI
├─ ComfyUI (GPU)
└─ lokale Daten / Queues

---

## 3. Nodes

### NODE B – Windows RTX Workstation
**Rolle:** Haupt‑Worker / Backend  
**Status:** aktiv

- FastAPI Backend
- ComfyUI GPU‑Pipeline
- lokale Modelle
- lokale Datenhaltung (SQLite, Filesystem)

**Ports:**
- 8030 – aktives Rescue‑Backend
- 8188 – ComfyUI
- 4321 – Frontend Dev (lokal)

---

### NODE D – Debian Laptop
**Rolle:** Infrastruktur‑Hub  
**Status:** aktiv (24/7)

- Cloudflare Tunnel
- SSH‑Hub
- Orchestrator‑Fallback
- Watchdog‑Dienste

---

### NODE A – Google Cloud VM (optional)
**Rolle:** Brain / Orchestrator  
**Status:** geplant

- zentrale KI‑Logik
- Agenten‑Koordination
- nur aktiv bei Bedarf

---

### NODE C – GPU Cloud (RunPod o. Ä.)
**Rolle:** On‑Demand Rendering  
**Status:** geplant

- große Video‑/GPU‑Jobs
- hartes Kosten‑Limit
- niemals Always‑On

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

---

## 8. Änderungs‑Policy

- Architekturänderungen → **hier zuerst**
- README bleibt Überblick
- Code nur nach Arch‑Anpassung

---

**Leitsatz:**  
> *Stabilität vor Features. Transparenz vor Cleverness.*
