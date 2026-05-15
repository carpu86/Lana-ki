# API_CONTRACT.md — Lana KI Orchestrator API

**Base URL (lokal):** `http://192.168.178.101:8024`  
**Base URL (public):** `https://gateway.lana-ki.de`

---

## Change-Log

| Version | Datum      | Änderung                                    |
|---------|------------|---------------------------------------------|
| 1.0.0   | 2025-05-15 | Initial – alle Kernendpunkte definiert       |

---

## Endpunkte

### `GET /health`

Systemstatus aller Dienste (P0 / P1 / P2).

**Response:**
```json
{
  "ok": true,
  "time": "2025-05-15T17:00:00Z",
  "p0": {
    "lm_studio": true,
    "comfyui": true
  },
  "p1": {
    "azure": true,
    "gemini": true
  },
  "p2": {
    "runpod": true
  }
}
```

| Priorität | Dienste             | Bedeutung                    |
|-----------|---------------------|------------------------------|
| P0        | LM Studio, ComfyUI  | Kritisch – lokal, Zero-Cost  |
| P1        | Azure, Gemini       | Wichtig – Cloud-Fallback     |
| P2        | RunPod              | Optional – Burst/Fallback    |

---

### `POST /chat`

Chat-Anfrage an einen KI-Companion.

**Request Body:**
```json
{
  "girl_id": "luna",
  "message": "Hallo, wie geht es dir?",
  "temperature": 0.7,
  "user_id": "user_123",
  "system_prompt_override": null
}
```

| Feld                   | Typ    | Pflicht | Default | Beschreibung                          |
|------------------------|--------|---------|---------|---------------------------------------|
| `girl_id`              | string | ✅      | —       | ID des Companion-Characters           |
| `message`              | string | ✅      | —       | Nachricht des Users                   |
| `temperature`          | float  | ❌      | 0.7     | Sampling-Temperatur (0.0–2.0)         |
| `user_id`              | string | ✅      | —       | Eindeutige User-ID                    |
| `system_prompt_override` | string | ❌   | null    | Überschreibt System-Prompt (Admin)    |

**Response:**
```json
{
  "reply": "Mir geht es gut, danke!",
  "tokens_used": 142,
  "provider": "lm_studio"
}
```

---

### `POST /image`

Bild-Generierung via ComfyUI (lokal) oder RunPod (Fallback).

**Request Body:**
```json
{
  "prompt": "beautiful woman, portrait, photorealistic",
  "negative_prompt": "blurry, deformed",
  "width": 512,
  "height": 512,
  "steps": 20,
  "girl_id": "luna"
}
```

| Feld              | Typ    | Pflicht | Default       | Beschreibung                          |
|-------------------|--------|---------|---------------|---------------------------------------|
| `prompt`          | string | ✅      | —             | Positiver Prompt                      |
| `negative_prompt` | string | ❌      | `""`          | Negativer Prompt                      |
| `width`           | int    | ❌      | 512           | Breite in Pixel (max 512)             |
| `height`          | int    | ❌      | 512           | Höhe in Pixel (max 512)               |
| `steps`           | int    | ❌      | 20            | Diffusion Steps (max 30)              |
| `girl_id`         | string | ❌      | null          | Optional – für Kontext                |

**Response:**
```json
{
  "url": "https://...",
  "provider": "comfyui",
  "metadata": {
    "width": 512,
    "height": 512,
    "steps": 20,
    "prompt_id": "abc123"
  }
}
```

---

### `GET /memory/{user_id}/{girl_id}`

Letzten N Nachrichten aus dem Qdrant-Gedächtnis abrufen.

**Path Parameter:**

| Parameter  | Typ    | Beschreibung         |
|------------|--------|----------------------|
| `user_id`  | string | User-Identifikator   |
| `girl_id`  | string | Character-ID         |

**Query Parameter:**

| Parameter | Typ | Default | Beschreibung                  |
|-----------|-----|---------|-------------------------------|
| `n`       | int | 20      | Anzahl der letzten Nachrichten |

**Response:**
```json
[
  {
    "role": "user",
    "content": "Hallo!",
    "timestamp": 1715000000.0
  },
  {
    "role": "assistant",
    "content": "Hallo! Schön von dir zu hören.",
    "timestamp": 1715000005.0
  }
]
```

---

### `PUT /memory/{user_id}/{girl_id}`

Nachricht manuell in das Gedächtnis schreiben.

**Path Parameter:** wie GET

**Request Body:**
```json
{
  "role": "user",
  "content": "Ich mag Pizza.",
  "metadata": {}
}
```

**Response:**
```json
{
  "ok": true
}
```

---

### `POST /mcp`

MCP Agent Request — Streamable-HTTP MCP-Protokoll.

**Request Body:**
```json
{
  "agent": "companion",
  "user_id": "user_123",
  "girl_id": "luna",
  "action": "respond",
  "payload": {
    "message": "Was machst du gerade?"
  }
}
```

| Feld      | Typ    | Pflicht | Beschreibung                              |
|-----------|--------|---------|-------------------------------------------|
| `agent`   | string | ✅      | `"companion"` oder `"intent"`             |
| `user_id` | string | ✅      | User-Identifikator                        |
| `girl_id` | string | ❌      | Character-ID (bei `companion`)            |
| `action`  | string | ✅      | Aktion (`respond`, `proactive`, `mood`)   |
| `payload` | object | ✅      | Aktions-spezifische Daten                 |

**Response:** Streaming Text/JSON

---

## Fehler-Codes

| HTTP-Code | Bedeutung                              |
|-----------|----------------------------------------|
| 200       | Erfolg                                 |
| 422       | Validierungsfehler (z.B. age < 18)     |
| 503       | Alle Provider nicht erreichbar         |
| 500       | Interner Fehler                        |
