# LANA-KI MASTER BLUEPRINT 2026

## 1. PRODUKTPOSITIONIERUNG
Das Kernprodukt ist kein generischer Bot-Marktplatz, sondern eine Plattform für fotorealistische, erinnerungsfähige, individuelle AI-Companions.

### Zielmodell
- Jedes Girl ist ein eigener Charakter
- Jedes Girl hat ein eigenes Langzeitgedächtnis
- Textchat ist im Basiszugang enthalten
- Bilder, Spezialmodi, Sprachnachrichten, Videos und exklusive Szenen sind Premium
- Die Charaktere sollen wie echte Menschen wirken, nicht wie Anime-Avatare oder generische Stock-Bots

---

## 2. KERNLOGIK DES GESCHÄFTSMODELLS

### Basis-Abo
Enthalten:
- unbegrenzter oder großzügiger Textchat
- ein einzelnes dauerhaftes Charakter-Gedächtnis pro Model
- persönliche Ansprache
- RAG-Erinnerungen
- Stimmige Charakterentwicklung
- normale Antwortgeschwindigkeit

### Premium-Abo / Add-ons
Zusätzlich freischaltbar:
- Bildgenerierung auf Anfrage
- exklusive Galerien
- Voice-Messages
- Videoloops / kurze Clips
- schnellere Queue
- tiefere Memory-Personalisierung
- Spezialrollen / Szenarien / Story-Arcs

### Paywall-Logik
Text = inklusive
Bilder / Medien / Spezialfunktionen = monetarisiert

Das ist stark, weil der User emotional gebunden wird, bevor er überhaupt bezahlt.

---

## 3. ARCHITEKTUR FÜR LANGZEITGEDÄCHTNIS PRO GIRL

### Grundprinzip
Nicht ein globales Gedächtnis für alle Girls, sondern:
- pro Character eine eigene Collection / Namespace
- pro User + pro Character getrennte Memory-Layer

### Empfohlenes Datenmodell
1. character_profiles
   - stabile Identität des Girls
   - Aussehen, Stimme, Temperament, Grenzen, Stil

2. user_character_sessions
   - Beziehung zwischen User und Charakter

3. memory_items
   - einzelne Erinnerungen
   - Gesprächsfakten
   - Vorlieben
   - Running Gags
   - vergangene Ereignisse

4. memory_summaries
   - verdichtete Langzeit-Zusammenfassungen

5. entitlement_flags
   - regelt: darf Text, Bild, Voice, Video, Premium-Szenen

### Memory-Scope
memory_namespace = "{user_id}:{character_id}"

Beispiel:
- user 781 + lana_classic
- user 781 + mia_red
- user 912 + lana_classic

Alle strikt getrennt.

---

## 4. WIE DIE GIRLS WIE ECHTE MENSCHEN WIRKEN

### A. Konsistentes Aussehen
Jedes Girl bekommt:
- feste Referenzbilder
- festen SDXL/Flux/ComfyUI Stil
- festen Prompt-Kern
- festen Negativprompt
- Seed-Strategie für Wiedererkennbarkeit
- optional LoRA / IP-Adapter Referenzen

### B. Menschliche Plausibilität
Pro Charakter definieren:
- Altersspanne
- Herkunft
- Sprachstil
- typische Reaktionen
- Interessen
- Tagesrhythmus
- emotionale Grundtemperatur
- visuelle Signatur

### C. Persistente Beziehung
Das Girl merkt sich:
- Namen
- Vorlieben
- Vorherige Gespräche
- Jubiläen
- Konflikte
- Insider
- Wünsche des Users

Dadurch entsteht der Eindruck echter Kontinuität.

---

## 5. BILD- UND MEDIENARCHITEKTUR

### Text standardmäßig lokal / günstig
- LM Studio auf 127.0.0.1:1234

### Bilder selektiv / Premium
- ComfyUI auf 127.0.0.1:8188
- nur bei Berechtigung auslösen
- Queue-basiert
- Generation Request an RTX-Node

### RTX-4060-8GB Schutzregeln
- --lowvram
- max 512x512
- kleine Batch Size
- Tiled VAE Decode
- keine unnötigen parallelen Jobs
- Video nur kurz und streng limitiert

### Medienpipeline
1. User fordert Bild an
2. Backend prüft Abo / Credits
3. Prompt Builder nimmt:
   - Charakterprofil
   - aktuellen Gesprächskontext
   - Szenen-Intent
4. Job an ComfyUI
5. Ergebnis wird unter user/character/media archiviert
6. Chat bekommt Media-Metadaten zurück

---

## 6. ABOSYSTEM EMPFOHLEN

### Tabellen / Objekte
- users
- subscriptions
- products
- product_features
- user_entitlements
- usage_events

### Feature Flags
- chat_text_included = true
- image_generation_enabled = false/true
- voice_enabled = false/true
- video_enabled = false/true
- premium_memory_depth = false/true

### Produkte
1. Free / Trial
   - limitierte Nachrichten
   - kein Bild
2. Basic
   - Text inklusive
   - ein oder mehrere Girls
3. Premium
   - Bilder
   - Voice
   - schnellere Antworten
4. Ultimate
   - Videos
   - Priorität
   - exklusive Szenen

---

## 7. BESTE USER EXPERIENCE FÜR DEIN MODELL

### Grid-Seite
Jede Karte zeigt:
- realistisches Hero-Bild
- Name
- Hook
- Badges
- Online-Status
- Memory-Level oder Beziehungsstatus

### Chat
- Cinematic Background
- leicht animierter Avatar
- Button für Text / Bild / Voice
- Premium-locked Aktionen mit klarer Freischaltlogik

### Monetarisierung ohne Nervfaktor
Nicht mit rohen Sperren nerven.
Stattdessen:
- Text läuft normal
- Bei Bildwunsch elegante Premium-Karte:
  "Ich kann dir ein persönliches Bild schicken, wenn du Premium aktivierst."

---

## 8. EMPFOHLENE BACKEND-ROUTEN

### Character
- GET /characters
- GET /characters/{id}
- GET /characters/{id}/media

### Chat
- POST /chat/send
- GET /chat/history/{userId}/{characterId}

### Memory
- GET /memory/{userId}/{characterId}/summary
- POST /memory/{userId}/{characterId}/ingest
- POST /memory/{userId}/{characterId}/compact

### Media
- POST /media/image/request
- POST /media/voice/request
- POST /media/video/request
- GET /media/job/{jobId}

### Billing
- GET /billing/products
- POST /billing/checkout
- GET /billing/entitlements/{userId}

---

## 9. EMPFOHLENE CHARAKTERSTRUKTUR

Jeder Charakter braucht:
- character_id
- display_name
- slug
- appearance_prompt_core
- appearance_negative_prompt
- personality_system_prompt
- voice_profile
- memory_policy
- premium_capabilities
- safe_render_profile
- thumbnail_path
- hero_path

---

## 10. REALISTISCHE LOOKS STATT KÜNSTLICHEM BOT-FEELING

### Dafür sorgen:
- fotografische Porträts
- natürliche Hautstruktur
- asymmetrische kleine Details
- echte Kleidung / echte Räume
- keine überladenen Effekte
- konsistente Lichtstimmung
- wiederkehrende Mikromerkmale

### Vermeiden:
- zufällige Stilwechsel
- widersprüchliche Gesichter
- zu sterile Beauty-Filter
- gleiche Pose bei allen Charakteren

---

## 11. TECHNISCHE EMPFEHLUNG FÜR DEINE KONKRETE INFRASTRUKTUR

### Windows Master
Pfad:
C:\Carpuncle Cloud\LanaApp

Aufgaben:
- LM Studio
- ComfyUI
- Bild- und Videojobs
- lokale Verwaltungs-Skripte

### Debian Laptop
IP:
100.67.27.13

Aufgaben:
- Master-Orchestrator
- API Hub
- Vision / Utilities
- Sync-Schicht
- Subscription Routing
- Memory APIs

### Google Brain
IP:
100.110.207.22

Aufgaben:
- Worker
- asynchrone Jobs
- Summaries
- Batch-Aufgaben
- Hintergrundverarbeitung

---

## 12. DIE WICHTIGSTE PRODUKTENTSCHEIDUNG

Ja:
- alle Girls sollen wie echte Menschen aussehen
- jedes Girl braucht eigenes Langzeitgedächtnis
- Text muss im Kauf inklusive sein
- Bilder und mehr müssen Abo-/Feature-gesteuert sein

Das ist die richtige Richtung.

Denn:
- Text erzeugt Bindung
- Gedächtnis erzeugt Loyalität
- Bilder erzeugen Conversion
- Voice erzeugt Suchtpotenzial
- Videoloops erzeugen Premium-Wahrnehmung

---

## 13. NÄCHSTER BAUSCHRITT

Empfohlene Reihenfolge:
1. Charakter-/Memory-Datenmodell finalisieren
2. Entitlement-System einbauen
3. Chat-API an Memory-Scope koppeln
4. Bild-Paywall implementieren
5. Frontend-Cards/Chat cineastisch umbauen
6. Voice ergänzen
7. Video zuletzt

---

## 14. KLARE PRODUKTREGEL IN EINEM SATZ

Jeder User chattet im Basispaket mit fotorealistischen, konsistenten AI-Girls mit eigenem Langzeitgedächtnis; Bilder, Voice, Videos und Spezialfunktionen werden pro Charakter oder Abo gezielt monetarisiert.
