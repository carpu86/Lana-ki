# 🧰 LANA‑KI – Scripts

Dieses Verzeichnis ist für **Automatisierungs‑, Operations‑ und Wartungs‑Skripte**
des gesamten LANA‑KI‑Systems vorgesehen.

Aktuell enthält es **keine produktiven Skripte**, sondern definiert den Zweck
und die Regeln für zukünftige Inhalte.

---

## 🎯 Zweck

Scripts in diesem Ordner dienen u. a. für:

- Infrastruktur‑Checks
- Health‑Diagnosen
- Start / Stop von Diensten
- Cloudflare‑Patches
- Backup‑ & Restore‑Routinen
- Sync zwischen Nodes

---

## 🧱 Erwartete Script‑Typen

- **PowerShell (`.ps1`)** – primär (Windows / Ops)
- **Shell (`.sh`)** – optional (Linux / Debian Node)
- **Python Helper** – nur wenn sinnvoll

---

## ⚠️ WICHTIGE REGELN

- ✅ Scripts müssen **copy‑paste‑fähig** sein
- ✅ Keine manuelle Datei‑Bearbeitung voraussetzen
- ✅ Idempotent (mehrfach ausführbar)
- ❌ Keine Secrets im Klartext
- ❌ Kein interaktiver Editor (nano, vi, notepad etc.)
- ✅ Backups vor Änderungen

---

## 🔐 Secrets & Konfiguration

- Scripts lesen Konfiguration **nur über Environment**
- `.env` Dateien gehören **nicht** in dieses Repository
- Langfristiges Ziel: **1Password CLI Injection**

---

## 🧠 Philosophie

> Automatisierung schlägt Dokumentation –  
> aber **Dokumentation erklärt Automatisierung**.

---

**Status:** vorbereitet  
