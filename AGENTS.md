# AGENTS.md — Lana KI Codex-Anweisungen

Vollständige Betriebsanweisungen für alle KI-Agenten und Automatisierungs-Skripte
die in diesem Repository arbeiten.

---

## Pfade & Verzeichnisse

| Bezeichnung       | Pfad                                   |
|-------------------|----------------------------------------|
| Lana Root         | `\\CARPUNCLE-PC\Lana KI`               |
| Git Drive         | `\\CARPUNCLE-PC\Lana KI\Lana Git`      |
| User Root         | `C:\Carpuncle Cloud\carpuncle.V6`      |
| Tools             | `C:\Carpuncle Cloud\Tools`             |
| .env              | `C:\Carpuncle Cloud\.env`              |

---

## Dienste & Ports

| Dienst              | Adresse                                        | Zweck                              |
|---------------------|------------------------------------------------|------------------------------------|
| LM Studio           | `http://127.0.0.1:1234/v1`                     | Lokale LLM-Inferenz (OpenAI-kompatibel) |
| ComfyUI             | `http://127.0.0.1:8188`                        | Lokale Bildgenerierung (RTX 4060) |
| Lana Orchestrator   | `http://192.168.178.101:8024`                  | FastAPI Master-API                 |
| Cloudflare Tunnel   | `https://gateway.lana-ki.de`                   | Public Gateway                     |
| Azure OpenAI        | `https://lana-ki-resource.cognitiveservices.azure.com/` | Cloud-LLM Fallback 1     |
| Gemini              | `generativelanguage.googleapis.com`            | Cloud-LLM Fallback 2               |
| Groq                | `api.groq.com`                                 | Cloud-LLM Fallback 3               |
| OpenAI              | `api.openai.com`                               | Cloud-LLM Fallback 4               |
| RunPod              | Aus .env (`NODE_*_RUNPOD_ENDPOINT_URL`)        | Bild-Fallback                      |
| Qdrant              | `http://localhost:6333`                        | Vektor-Gedächtnis                  |
| Storage Box         | `u585979.your-storagebox.de` Port 23           | Cold Storage / Backup              |

---

## LLM Fallback-Chain (Reihenfolge)

1. **LM Studio** `127.0.0.1:1234` — lokal, Zero-Cost, höchste Priorität
2. **Azure OpenAI** (westeurope)
3. **Gemini 2.5 Flash**
4. **Groq**
5. **OpenAI**

## Bild Fallback-Chain (Reihenfolge)

1. **ComfyUI** `127.0.0.1:8188` — lokal, RTX 4060, 8 GB VRAM
2. **RunPod API**

---

## Strikte Regeln

### Kein Ollama
- **NIEMALS** Ollama installieren oder verwenden.
- Lokale LLM-Inferenz ausschließlich über **LM Studio** (`127.0.0.1:1234`).

### Altersvalidierung (hartkodiert)
- `CharacterSheet.age` **MUSS >= 18** sein.
- Validierung in `CharacterSheet.__post_init__()` — wirft `ValueError` wenn `age < 18`.
- Diese Regel ist unveränderlich und darf von keinem Agenten umgangen werden.

### .env — Append-Only
- `.env` unter `C:\Carpuncle Cloud\.env` **NIEMALS** löschen, leeren oder blind überschreiben.
- Erlaubt: Append, gezieltes Patchen, Rotation mit Backup + Timestamp.
- **Nur Lana (Thomas) darf Keys rotieren.**
- Vor jeder Änderung an `.env` immer Backup mit Timestamp erstellen:
  ```powershell
  Copy-Item "C:\Carpuncle Cloud\.env" "C:\Carpuncle Cloud\.env.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
  ```

### Backup vor Datei-Änderungen
- Vor **jeder** Änderung an bestehenden Konfigurationsdateien Timestamp-Backup erstellen.
- Schema: `<datei>.bak_<yyyyMMdd_HHmmss>`

### Bestehende Dateien
- Dateien in `backend/` und `docs/` **nicht löschen** — nur neue hinzufügen.
- Bestehende API-Endpunkte nicht entfernen, nur ergänzen.

### Secrets
- Alle Provider-Keys aus `.env` via `os.getenv()` laden.
- **Niemals** Secrets hardcoden oder in Git committen.
- `.env`-Dateien sind in `.gitignore` eingetragen.

### VRAM-Limits (RTX 4060, 8 GB)
- ComfyUI max **512×512** Pixel.
- ComfyUI max **30 Steps**.
- TiledVAE verwenden wenn verfügbar.

---

## Infrastruktur-Nodes

| Node   | Rolle                          | Zugang                   |
|--------|--------------------------------|--------------------------|
| NODE B | Windows RTX Desktop (GPU)      | CARPUNCLE-PC lokal        |
| NODE D | Debian Laptop (Tunnel / Hub)   | `carpu@192.168.178.101`  |
| NODE A | Hetzner Public Gateway         | `carpu@178.105.45.252`   |
| COLD   | Hetzner Storage Box            | `u585979@u585979.your-storagebox.de:23` |

---

## Deployment

- Orchestrator läuft auf **NODE D** (Laptop): `192.168.178.101:8024`
- Erreichbar via Cloudflare Tunnel: `https://gateway.lana-ki.de`
- Start-Kommando: `uvicorn backend.main:app --host 0.0.0.0 --port 8024`
