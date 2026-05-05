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

```
Internet
│
▼
Cloudflare DNS / Pages / Tunnel
│  Domain: lana-ki.de
▼
┌──────────────────────────────────────┐
│ Debian Laptop – NODE D               │
│ Stammhirn / Hub / Master-Orchestrator│
│ Tailscale: 100.67.27.13              │
│ FastAPI Orchestrator: :8024          │
│ LLaVA Vision: :8080                  │
└──────────────────────────────────────┘
│  Tailscale Mesh (100.x.x.x)
▼
┌──────────────────────────────────────┐
│ Windows PC – NODE B                  │
│ RTX-Muskel / Master-Worker           │
│ Lokal: 127.0.0.1                     │
│ LM Studio: :1234                     │
│ ComfyUI: :8188                       │
│ FastAPI Backend: :8030               │
│ Pfad: C:\Carpuncle Cloud\LanaApp     │
└──────────────────────────────────────┘
│  Tailscale Mesh (100.x.x.x)
▼
┌──────────────────────────────────────┐
│ Google Cloud VM – NODE A             │
│ Brain / Worker                       │
│ Tailscale: 100.110.207.22            │
└──────────────────────────────────────┘
```

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

## 🖥️ Nodes & IPs

| Node | Bezeichnung | Rolle | Adresse / IP | Wichtige Ports |
|------|-------------|-------|-------------|----------------|
| NODE B | Windows PC | Master / RTX‑Muskel | Lokal: `127.0.0.1` | LM Studio `:1234`, ComfyUI `:8188`, FastAPI `:8030` |
| NODE D | Debian Laptop | Stammhirn / Hub | Tailscale: `100.67.27.13` | Orchestrator `:8024`, LLaVA `:8080` |
| NODE A | Google Cloud VM | Brain / Worker | Tailscale: `100.110.207.22` | – |

> **Netzwerk‑Hinweis:** Alle Knoten kommunizieren **ausschließlich über das Tailscale‑Mesh** (`100.x.x.x`).  
> Keine öffentlichen Internet‑IPs verwenden. Lokale LAN‑IPs (`192.168.x.x`) sind nur für SMB‑Freigaben zulässig.

---

## 🔌 Dienste & API‑Endpunkte

| Dienst | URL | Node | Beschreibung |
|--------|-----|------|-------------|
| FastAPI Backend | `http://127.0.0.1:8030` | NODE B | Haupt‑Backend |
| LM Studio | `http://127.0.0.1:1234` | NODE B | Lokale LLM‑Inferenz (RTX) |
| ComfyUI | `http://127.0.0.1:8188` | NODE B | Bildgenerierung (GPU) |
| Master‑Orchestrator | `http://100.67.27.13:8024` | NODE D | FastAPI Multi‑Agent‑Routing |
| LLaVA Vision | `http://100.67.27.13:8080` | NODE D | Bild‑Verstehen / Vision |
| Frontend | `https://lana-ki.de` | Cloudflare Pages | Astro‑Webapp |

---

## 📂 Pfad‑Konventionen

| Regelung | Detail |
|----------|--------|
| ✅ Primärer Projektpfad | `C:\Carpuncle Cloud\LanaApp` |
| ✅ Lokale SMB‑Freigabe | `\\localhost\Lana KI` bzw. `\\127.0.0.1\Lana KI` |
| ✅ Netzwerk‑SMB‑Freigabe | `\\192.168.178.100\Lana KI` |
| ❌ `T:\` verboten | Gemappte Laufwerke **niemals** in Code oder Docs hardcoden |
| ❌ Externe IPs verboten | Keine öffentlichen Internet‑IPs; LAN (`192.168.x.x`) nur für SMB‑Freigaben |

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
