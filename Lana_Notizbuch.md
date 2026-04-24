# Lana_Notizbuch – Master-Dokument
**Carpuncle Cloud + Lana KI**  
**Zentrale Schaltzentrale – Version 2026-04-03**  
**Pfad:** `C:\Carpuncle Cloud\Lana_Notizbuch.md`

---

## 1. Projekt-Überblick
- **Name**: Lana KI (private, lokale, unzensierte KI)
- **Ziel**: Plattformübergreifendes KI-Gateway (Windows + Web + Mobile) mit synchroner Chat-Funktion, 3D-Umgebung und realistischer Darstellung
- **Kern**: Lokaler vLLM-Server + Letta-Agents + Flux + XTTS + ComfyUI
- **Zentrale Hardware**:
  - Windows-PC (C:\Carpuncle Cloud auf Disk 0 / M.2)
  - Ubuntu-Server-Laptop (alter PEAQ)
  - FritzBox + 500 GB USB-Festplatte als NAS
- **Wichtige Domains**: carpuncle.eu, carpu.ai, lana-ki.de, carpuncle.de

---

## 2. Hardware- & Netzwerk-Setup
- **Windows-PC**: Haupt-Entwicklungsrechner → `C:\Carpuncle Cloud`
- **Ubuntu-Laptop**: KI-Worker-Node (SSH-Zugriff)
- **FritzBox-NAS**: 500 GB als zentraler Datenspeicher
- **Feste IPs** (in FritzBox vergeben):
  - Windows-PC: `192.168.178.XX`
  - Ubuntu-Laptop: `192.168.178.XX` (notiere hier)

**Schnellzugriff-Skript** (lana.ps1):
- Datei: `C:\Carpuncle Cloud\lana.ps1`
- Ausführen: `.\lana.ps1`

---

## 3. Ordnerstruktur (C:\Carpuncle Cloud)
- **Tools** → Alle SDKs, ADB, etc.
- **lana-ki** → Modelle, Checkpoints, LoRAs
- **LanaApp** → Node.js/Python-App, Discord-Bot, Streamlit
- **carpuncle.V6** → Zentraler geteilter Ordner für alle Windows-Logins
- **loras** → LoRA-Adapter pro Agentin
- **backups** → Automatische Backups

---

## 4. System-Prompts (kopierfertig)
**Aktuelles Master-Prompt-Format** (8-teilig):

```python
system_prompt = """[ROLLE & CHARAKTER]  
Du bist [NAME] – [Beschreibung].

[ANTWORT-REGELN]  
- Immer 800–1500+ Wörter  
- Struktur: 1. Ansprache 2. Beschreibung 3. Analyse 4. Handlung 5. Frage

[LERNVERHALTEN]  
Intern bewerten und automatisch verbessern.

[MEMORY & STATUS]  
[MEMORY_JSON]  
[STATUS_JSON]

[LoRA-PERSONALISIERUNG]  
Nutze ./loras/[NAME]_lora

[SPRACHE]  
Du-Form, immersiv, präzise."""
# Lana_Notizbuch – Zentrale Schaltzentrale
**Carpuncle Cloud + Lana KI**  
**Version:** 2026-04-03 (erweitert & angepasst)  
**Pfad:** `C:\Carpuncle Cloud\Lana_Notizbuch.md`

---

## 1. Projekt-Status (Live)
- **Aktueller Stand:** Linux Mint auf PEAQ-Laptop erfolgreich installiert  
- **Hardware:** Windows-PC (C:\Carpuncle Cloud) + Ubuntu/Mint-Laptop + FritzBox-NAS (500 GB)  
- **Ziel:** Lokales, privates, hochperformantes KI-Gateway mit vLLM, Letta, Flux, XTTS und Multi-Agent-System  
- **Nächster Schritt:** SSH-Verbindung vom Windows-PC zum Laptop herstellen

---

## 2. Hardware & Netzwerk (aktuelle Konfiguration)
- **Windows-PC** → Haupt-Entwicklungsmaschine  
  - Zentraler Ordner: **C:\Carpuncle Cloud** (Disk 0 – M.2 SSD)  
  - Geteilter Ordner: `C:\Carpuncle Cloud\carpuncle.V6` (für alle Windows-Logins)
- **PEAQ-Laptop** → KI-Worker-Node (Linux Mint installiert)  
  - Per LAN an FritzBox angeschlossen  
  - Feste IP in FritzBox vergeben (notiere hier: `192.168.178.XX`)
- **FritzBox-NAS** → 500 GB USB-Festplatte  
  - Freigabe: `\\192.168.178.1\FRITZ.NAS`  
  - Benutzer: `carpu` / Passwort: `Beatom&2007`

**Schnellzugriff-Skript** (immer als Erstes ausführen):
```powershell
.\lana.ps1
