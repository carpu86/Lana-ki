# ⚙️ LANA‑KI – Backend

Dieses Verzeichnis beschreibt das **Backend‑Konzept** von LANA‑KI.  
Es enthält **aktuell keinen produktiven Code**, sondern dient der Struktur
und Dokumentation.

---

## 🎯 Aufgabe des Backends

Das Backend ist die **zentrale Schicht** zwischen:

- Frontend / Companion UI
- Telegram Bot
- KI‑Agenten
- ComfyUI GPU‑Worker
- Orchestrator / Brain

---

## 🧱 Technologie (Ist / Soll)

- **Framework:** FastAPI (Python)
- **Kommunikation:** REST / später WebSocket
- **Job‑Handling:** Queue‑basiert
- **Persistenz:** SQLite + Filesystem
- **Deployment:** lokal (Windows), optional Cloud

---

## 🚑 Aktueller Status

- Aktiver stabiler Fallback:
  - **Rescue Backend**
  - Port **8030**
  - Health‑Endpoint aktiv
- Vollständiges Production‑Backend:
  - **in Vorbereitung**
  - wird dieses Verzeichnis später füllen

---

## 🔌 Wichtige Endpunkte (konzeptionell)

| Pfad | Zweck |
|----|----|
| `/api/health` | Systemstatus |
| `/api/chat` | Chat / Companion |
| `/api/generate/image` | Bild‑Jobs |
| `/api/jobs/*` | Job‑Status |
| `/api/admin/*` | Admin / Ops |

(*Details siehe docs/ARCHITECTURE.md*)

---

## 🔐 Konfiguration

- **Keine `.env`‑Dateien im Repository**
- Backend liest Konfiguration über:
  - `.env.runtime`
  - `.env.ai`
  - `.env.ops`
- Langfristig: **1Password CLI Injection**

---

## ⚠️ Wichtige Regeln

- Kein Hardcoding von Secrets
- Kein lokaler Pfad im Code ohne Abstraktion
- Health‑Endpoint ist Pflicht
- Jede neue API → Dokumentation zuerst

---

**Status:** vorbereitet  
**Dieses Verzeichnis wird später echten Code aufnehmen.**
