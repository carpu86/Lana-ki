# 🌌 LANA‑KI

**Hybride, lokale & cloud‑erweiterbare Multi‑Agent‑KI‑Plattform**  
📍 Germany | 🖥️ Local‑First | ☁️ Cloud‑Fallback | 🤖 AI‑Companions

---

## 🚀 Kurzüberblick

**LANA‑KI** ist eine modulare KI‑Plattform mit Fokus auf:

- 🧠 **Multi‑Agent‑Architektur**
- 🖥️ **Lokale GPU‑Ausführung (RTX‑Workstation)**
- 🌐 **Cloudflare‑basiertes Public Routing**
- 🧩 **FastAPI‑Backend**
- 🎨 **ComfyUI Bild‑ & Asset‑Pipeline**
- 💬 **Telegram‑Bot & Web‑Companion**
- 🔐 **Strikte Secret‑Trennung (kein Hardcoding)**

❗ Dieses Repository enthält **KEINE Secrets**, **KEINE Tokens**, **KEINE .env‑Dateien**.

---

## 🧱 System‑Architektur (Kurzfassung)
Internet
│
▼
Cloudflare DNS / Tunnel
│
▼
┌──────────────────────────────┐
│ Debian / Laptop (NODE D)     │
│ 24/7 Hub + Tunnel + Watchdog │
└──────────────────────────────┘
│
▼
┌──────────────────────────────┐
│ Windows RTX Workstation      │
│ FastAPI + ComfyUI + GPU      │
└──────────────────────────────┘
│
├─ optional Cloud Brain (GCP)
└─ optional GPU Burst (RunPod)

---

## 🧩 Hauptkomponenten

- **Backend:** FastAPI (Python)
- **Frontend:** Astro / Vite
- **Bildpipeline:** ComfyUI (lokal, GPU)
- **Agents:** Multi‑Port‑Agenten (8020–8024)
- **Routing:** Cloudflare DNS & Tunnel
- **Bot:** Telegram (Chat, Credits, Assets)
- **Storage:** SQLite + Filesystem Queue
- **Secrets:** `.env`‑Split / 1Password CLI (nicht im Repo)

---

## 🖥️ Nodes

| Node | Rolle | Status |
|----|----|----|
| NODE B | Windows RTX Desktop (GPU Worker) | ✅ aktiv |
| NODE D | Debian Laptop (Tunnel / Hub) | ✅ aktiv |
| NODE A | Google Cloud Brain | ⏸ optional |
| NODE C | RunPod GPU Burst | ⏳ geplant |

---

## ⚠️ Sicherheits‑Regeln (WICHTIG)

Dieses Repository darf enthalten:
- ✅ Code
- ✅ Dokumentation
- ✅ Beispiel‑Konfigurationen (`.env.example`)

Dieses Repository darf **NICHT** enthalten:
- ❌ `.env`
- ❌ `.env.*`
- ❌ Tokens / API‑Keys
- ❌ SSH‑Keys
- ❌ Cloudflare Credentials
- ❌ 1Password Exporte

---


## ✅ Canonical Workspace Baseline (verbindlich)

### Erlaubte lokale Hauptanker

- `RuntimeRoot`: `C:\Carpuncle Cloud\Lana KI`
- `Git-Ledger`: `C:\Carpuncle Cloud\Lana KI\Lana Git`
- `DokuRoot`: `C:\Carpuncle Cloud\Lana KI\docs`
- `Aktive .env`: `C:\Carpuncle Cloud\Lana KI\.env`
- `UserRoot`: `C:\Carpuncle Cloud\carpuncle.V6`
- `ToolRoot`: `C:\Carpuncle Cloud\Tools`

### Nicht erlaubt (Legacy)

- `T:\...` Pfade
- `C:\Carpuncle Cloud\LanaApp` als produktiver Root

### Architektur-Nodes (kanonisch)

- **NODE A (Master / Public Edge):** Cloudflare Tunnel Gateway `gateway.lana-ki.de`, FastAPI Backend `:8030`
- **NODE B (Windows RTX 4060):** lokale Inferenz (`127.0.0.1:1234`) + ComfyUI (`127.0.0.1:8188`), LAN `192.168.178.100`
- **NODE C (RunPod / Hetzner CPX42):** Burst-Cloud-Worker
- **NODE D (Debian Hub):** Orchestrator / Monitoring / Ingress, LAN `192.168.178.101`
- **NAS (FritzBox):** `192.168.178.1`, Cold Storage / Backup / SQLite-Archive

### Betriebsregel

- `.env`, Vaults und Secret-Archive werden **nie** nach Git synchronisiert.
- Lokale GitHub-Arbeit nur im `Git-Ledger`-Pfad.

---
## 📄 Lizenz

Aktuell **keine Open‑Source‑Lizenz**.  
Privates/kommerzielles Projekt – Nutzungsrechte vorbehalten.

---

## 🧭 Roadmap (Auszug)

- ✅ Image Generation (ComfyUI)
- ✅ Rescue‑Backend
- ⏳ Production Backend
- ⏳ Companion Web‑UI
- ⏳ Video / AnimateDiff
- ⏳ Multi‑Agent Orchestrator
- ⏳ Monetarisierung (Telegram / Credits)

---

## 🧠 Grundregel

> **Erst stabil lokal, dann Tunnel, dann Web, dann Geld.**

---

**Status:** aktiv  
**Owner / Architect:** Thomas Heckhoff  
**Project:** Lana‑KI
