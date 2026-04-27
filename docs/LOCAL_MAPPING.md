# 🧭 LANA-KI – Local Mapping

Stand: 20260427-093207

Diese Datei beschreibt die lokale Arbeitsstruktur auf dem Windows-Node.

---

## 📁 Lokale Hauptpfade

| Zweck | Pfad |
|------|-----|
| AppRoot | C:\Carpuncle Cloud\LanaApp |
| Git-Repo | C:\Carpuncle Cloud\LanaApp\lana-ki |
| Logs | C:\Carpuncle Cloud\LanaApp\logs |
| Rescue Backend | C:\Carpuncle Cloud\LanaApp\rescue_backend |
| Python venv | C:\Carpuncle Cloud\LanaApp\venv |

---

## 🌐 Public Status

| URL | Status |
|-----|--------|
| https://lana-ki.de/api/health | ✅ OK |
| https://lana-ki.de/ | ✅ OK |
| https://www.lana-ki.de/api/health | ✅ OK |
| https://www.lana-ki.de/ | ✅ OK |

---

## ☁️ Cloudflare Tunnel

| Feld | Wert |
|------|------|
| Tunnel Name | lana-ki-main |
| Tunnel ID | d051bcc0-f66c-41ce-bccd-c6cf3e01ab59 |
| Tunnel Target | d051bcc0-f66c-41ce-bccd-c6cf3e01ab59.cfargotunnel.com |
| Windows Origin | http://192.168.178.100:8030 |
| Laptop Node | carpu@192.168.178.103 |

---

## 🧠 Backend Status

Aktueller Public Health Mode:

| Feld | Wert |
|------|------|
| mode | rescue |
| service | lana-rescue-backend |
| aiortc_loaded | true |
| brain_loaded | false |
| brain_error | No module named gemini_brain |

Nächster technischer Schritt: echtes gemini_brain Modul finden und in den Backend-Startpfad integrieren.

---

## 🔐 Secrets-Regel

Cloudflare-, Azure-, Gemini-, Telegram- und Payment-Secrets werden nicht ins Git-Repository geschrieben.