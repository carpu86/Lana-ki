# 🖥️ LANA‑KI – Frontend

Dieses Verzeichnis beschreibt die **Frontend‑Schicht** von LANA‑KI.
Aktuell ist es **konzeptionell**, nicht produktiv befüllt.

---

## 🎯 Aufgabe des Frontends

Das Frontend ist die **primäre Benutzeroberfläche** für:

- AI‑Companion‑Interaktion
- Bild‑ & Medien‑Requests
- Account‑ / Credit‑Status
- Mobile & Desktop Nutzung

---

## 🧱 Technische Richtung (Soll)

- **Framework:** Astro / Vite
- **Design:** Mobile‑First, minimalistisch
- **Anbindung:** FastAPI Backend
- **Auth:** geplant (nicht öffentlich im Code)
- **Realtime:** optional via WebSocket

---

## 📱 Ziel‑Oberflächen

- Companion Chat Web‑UI
- Image Creation UI
- Character‑Profile
- Admin‑/Status‑Views (später)

---

## 🧪 Aktueller Stand

- Lokaler Dev‑Server (experimentell)
- Öffentliche UI **noch nicht aktiv**
- Öffentliche Web‑Präsenz aktuell über Backend‑Fallback

Dieses Verzeichnis wird später die produktive Web‑App enthalten.

---

## 🔐 Sicherheits‑Regeln

- Keine API‑Keys im Frontend
- Keine Secrets im Build
- Alle sensitiven Logiken serverseitig

---

## ⚠️ Wichtige Regel

> Frontend ist **austauschbar** – Backend & Daten nicht.

---

**Status:** vorbereitet  
**Implementierung folgt**
