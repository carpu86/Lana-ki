# 🤝 Contributing to LANA‑KI

Danke für dein Interesse an **LANA‑KI**.

Dieses Projekt folgt **strikten technischen und organisatorischen Regeln**,
um Stabilität, Sicherheit und langfristige Wartbarkeit zu gewährleisten.

---

## 🧠 Grundprinzipien

- **Local‑First vor Cloud**
- **Stabilität vor Features**
- **Dokumentation vor Implementierung**
- **Automatisierung vor manuellen Eingriffen**
- **Security jederzeit**

---

## 🚫 Was nicht akzeptiert wird

- Klartext‑Secrets (API‑Keys, Tokens, Passwörter)
- `.env` Dateien
- Hardcodierte Pfade ohne Abstraktion
- GUI‑only Lösungen ohne Script‑Fallback
- Änderungen ohne vorherige Dokumentation

---

## ✅ Erwartete Arbeitsweise

- Änderungen **erst dokumentieren**, dann implementieren
- Scripts müssen:
  - copy‑paste‑fähig sein
  - idempotent sein
  - Backups erstellen, bevor sie etwas ändern
- Keine interaktiven Texteditoren als Voraussetzung
  (`nano`, `vi`, `notepad` etc.)

---

## 🔐 Secrets & Konfiguration

- Secrets werden **niemals** versioniert
- Konfiguration erfolgt über:
  - `.env.runtime`
  - `.env.ai`
  - `.env.ops`
  - `.env.payments`
- Ziel: **Injection via 1Password CLI**

---

## 🌿 Branch‑ & Commit‑Regeln

- `main` ist stabil
- Saubere, beschreibende Commit‑Messages
- Dokumentations‑Änderungen sind jederzeit erlaubt
- Größere Umbauten → Architektur zuerst anpassen

---

## 🧪 Qualität & Stabilität

- Jeder neue Dienst benötigt:
  - einen definierten Port
  - einen Health‑Endpoint
- Öffentliche Erreichbarkeit ausschließlich über Cloudflare
- Logs dürfen **keine Secrets** enthalten

---

## 📌 Letzte Regel (wichtig)

> **Wenn etwas nicht dokumentiert ist, existiert es nicht.**

---

Danke fürs Mitbauen – bewusst, sauber und stabil.
