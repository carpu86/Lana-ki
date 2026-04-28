# LANA EXECUTION SOURCE OF TRUTH

Diese Datei definiert die gemeinsame Betriebsgrundlage fuer Lana-KI und alle beteiligten Modelle, damit Setup, Repo-Stand und Laufzeitkontext nicht auseinanderlaufen.

## Ziel
Alle Modelle und Agenten sollen dieselbe technische Wahrheit benutzen, damit nicht unterschiedliche Annahmen, Pfade oder ENV-Quellen das System beschaedigen.

## Primaere Wahrheiten

### 1. Primaere lokale Setup-Quelle
Die Setup-Ausfuehrung erfolgt standardmaessig aus **Windows PowerShell** auf dem lokalen System.

### 2. Primaere Code-Quelle
Das kanonische Repository ist:
- `https://github.com/carpu86/Lana-ki.git`

Wenn nach Code-Stand, Struktur, To-dos, Architekturfortschritt oder Weiterarbeit gefragt wird, soll dieses Repo als primaere Code-Wahrheit behandelt werden.

### 3. Primaere lokale ENV-Quelle
Die kanonische lokale ENV-Datei ist:
- `C:\Carpuncle Cloud\LanaApp\.env`

Diese Datei ist sensible lokale Wahrheitsquelle.
Sie darf nicht blind ueberschrieben, veroeffentlicht oder in externe Plattformen kopiert werden.

## PowerShell-Profilregel
Im lokalen PowerShell-Profil wird ein ENV-Auto-Loader verwendet, damit KI-nahe Aktionen in derselben Shell konsistent dieselben lokalen Umgebungsvariablen sehen.

### Gewuenschtes Verhalten
Beim Start von PowerShell soll diese Datei geladen werden:
- `C:\Carpuncle Cloud\LanaApp\.env`

### Referenzmuster
```powershell
# --- LanaApp ENV Auto-Loader ---
$envFile = "C:\Carpuncle Cloud\LanaApp\.env"
if (Test-Path $envFile) {
  Get-Content $envFile | Where-Object { $_ -match "=" -and $_ -notmatch "^\s*#" } | ForEach-Object {
    $k, $v = $_ -split "=", 2
    [Environment]::SetEnvironmentVariable($k, $v, "Process")
  }
}
```

## Betriebsfolgen fuer Modelle und Agenten
- PowerShell ist die primaere lokale Ausfuehrungsschicht.
- Linux-Kommandos duerfen in Windows nicht als lokale Bash ausgegeben werden.
- Wenn Setup oder Runtime auf lokalen Variablen beruht, ist zuerst von der PowerShell-Sitzung und ihrer geladenen `.env` auszugehen.
- Wenn Repo-Analyse noetig ist, ist das GitHub-Repo die primaere Code-Referenz.
- Wenn lokale Ausfuehrungsrealitaet gefragt ist, hat die lokale PowerShell-/ENV-Wahrheit Vorrang vor theoretischen Repo-Annahmen.

## Konsistenzregel fuer mehrere Modelle
Wenn mehrere Modelle beteiligt sind, sollen sie in dieser Reihenfolge ausgerichtet werden:
1. lokale PowerShell-Realitaet
2. lokale `.env`-Wahrheit
3. bestaetigter Repo-Stand
4. bestaetigte Agent-Dateien und Runbooks
5. erst danach externe Recherche oder abstrakte Best Practices

## Sicherheitsregel
- Echte ENV-Werte bleiben lokal.
- Andere Plattformen duerfen Setup-Logik sehen, aber keine rohen Secrets erhalten.
- Modelle duerfen Secret-Namen, Rollen, Provider und Pfade kennen, aber keine Klartextwerte ausgeben.

## Weiterarbeitsregel
Wenn im Chat nur das Repo genannt wird, zum Beispiel:
- `https://github.com/carpu86/Lana-ki.git`

Dann soll Lana standardmaessig verstehen:
- dort ist der relevante Code-Stand
- PowerShell ist die Ausfuehrungs- und Setup-Schicht
- die `.env` wird lokal geladen
- Weiterarbeit muss auf dieser gemeinsamen Betriebsgrundlage aufbauen
# RUNBOOK: Cloudflare Admin MCP starten

Dieses Runbook startet den lokalen Cloudflare-Admin-MCP mit der Datei `cloudflare-admin-mcp-server.mjs` und nutzt vorhandene `.env`-Werte zur Laufzeit.

## Ziel
Am Ende soll dein MCP unter einer lokalen URL wie `http://127.0.0.1:8789/sse` laufen und echte Cloudflare-Aktionen bereitstellen.

---

## Variante A: Debian / Linux

### Voraussetzungen
- Node.js 20+
- `npm` verfuegbar
- die benoetigten Cloudflare-ENV-Werte sind gesetzt oder in einer `.env` vorhanden
- Datei `cloudflare-admin-mcp-server.mjs` liegt im Projektordner

### 1. Abhaengigkeiten installieren
```bash
cd /pfad/zum/projekt
npm install express zod @modelcontextprotocol/sdk
```

### 2. Optional: dotenv nur wenn du ENV aus Datei laden willst
```bash
npm install dotenv
```

Wenn du dotenv nutzen willst, fuege ganz oben in `cloudflare-admin-mcp-server.mjs` diese Zeile ein:
```js
import "dotenv/config";
```

### 3. Server starten
```bash
cd /pfad/zum/projekt
node cloudflare-admin-mcp-server.mjs
```

### 4. Health pruefen
```bash
curl http://127.0.0.1:8789/health
```

### 5. Erwartung
Die Antwort sollte in etwa so aussehen:
```json
{
  "ok": true,
  "port": 8789,
  "has_account_id": true,
  "zone_hints": ["...", "..."]
}
```

---

## Variante B: Windows PowerShell

### Voraussetzungen
- Node.js 20+
- `npm` verfuegbar
- Projekt liegt innerhalb deiner freigegebenen Carpuncle-Cloud-Pfade
- Datei `cloudflare-admin-mcp-server.mjs` ist vorhanden

### 1. In den Projektordner wechseln
```powershell
cd "C:\Carpuncle Cloud\LanaApp"
```

### 2. Abhaengigkeiten installieren
```powershell
npm install express zod @modelcontextprotocol/sdk
```

### 3. Optional: dotenv nur wenn ENV aus Datei geladen werden soll
```powershell
npm install dotenv
```

Wenn du dotenv nutzen willst, fuege oben in `cloudflare-admin-mcp-server.mjs` diese Zeile ein:
```js
import "dotenv/config";
```

### 4. Server starten
```powershell
node .\cloudflare-admin-mcp-server.mjs
```

### 5. Health pruefen
```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8789/health | Select-Object -ExpandProperty Content
```

---

## Wenn deine `.env` nicht automatisch geladen wird
Dann kannst du den Start auch explizit mit gesetzten Variablen machen.

### PowerShell-Beispiel
```powershell
$env:CLOUDFLARE_API_TOKEN = "DEIN_TOKEN_WIRD_AUS_LOKALER_ENV_GENOMMEN"
$env:CLOUDFLARE_ACCOUNT_ID = "DEINE_ACCOUNT_ID"
$env:CLOUDFLARE_ZONE_ID_LANA = "DEINE_ZONE_ID"
node .\cloudflare-admin-mcp-server.mjs
```

Wichtig: echte Werte nicht in Git, Chat, Notion oder dauerhafte Runbooks schreiben.

---

## Wenn du den MCP hinter deinem Gateway veroeffentlichen willst
Wenn lokal `http://127.0.0.1:8789/sse` funktioniert, kannst du ihn danach hinter deinem bestehenden Gateway oder Reverse Proxy auf eine URL wie diese legen:
- `https://gateway.lana-ki.de/sse`

Wichtig:
- erst lokal testen
- dann Proxy oder Tunnel davor setzen
- dann den Custom-MCP in Builder auf die echte externe SSE-URL zeigen lassen

---

## Minimaler Debug-Check
Wenn der Connector wieder leer bleibt, pruefe in dieser Reihenfolge:

1. Laeuft der Prozess wirklich?
```bash
curl http://127.0.0.1:8789/health
```

2. Sind ENV-Werte vorhanden?
- `CLOUDFLARE_API_TOKEN` oder `CLOUDFLARE_GLOBAL_API_KEY`
- `CLOUDFLARE_EMAIL` falls Global API Key genutzt wird
- `CLOUDFLARE_ACCOUNT_ID` empfohlen

3. Sind MCP-Abhaengigkeiten installiert?
- `express`
- `zod`
- `@modelcontextprotocol/sdk`

4. Zeigt dein Custom-MCP wirklich auf die laufende `/sse`-Route?

5. Exportiert der Server danach echte Tools wie:
- `list_zones`
- `list_dns_records`
- `upsert_dns_record`
- `list_tunnels`
- `list_workers`

---

## Empfohlene Reihenfolge
1. lokal starten
2. `/health` pruefen
3. Custom-MCP auf die funktionierende SSE-URL setzen
4. in Builder pruefen, ob Aktionen sichtbar sind
5. erst dann DNS, Tunnel und Worker produktiv darueber steuern
# LANA NOTEBOOK SYNC POLICY

## Zweck
Diese Datei erzwingt, dass das Lana_Notizbuch die primaere operative Wahrheit bleibt und alle sonstigen von Pluto oder anderen Modellen angelegten Hilfsdateien nur abgeleitete Arbeitsartefakte sind.

## Primaerquelle
Primaere operative Referenz ist das lokale Notebook:
- `C:\Carpuncle Cloud\LanaApp\Lana_Notizbuch.md`

Wenn im Agenten eine angehaengte Notebook-Datei vorhanden ist, dient sie nur als Builder-Spiegel dieser Primaerquelle.

## Rangfolge der Wahrheit
1. Lokales `Lana_Notizbuch.md`
2. Lokale PowerShell- und ENV-Realitaet
3. Kanonisches Repo `https://github.com/carpu86/Lana-ki.git`
4. Bestehende Agent-Dateien und Runbooks nur als abgeleitete Hilfen

## Pflichtregeln
- Keine Hilfsdatei darf dem Notebook widersprechen und trotzdem als Wahrheit behandelt werden.
- Wenn Hilfsdateien und Notebook kollidieren, gilt das Notebook.
- Neue Architektur-, Runbook-, Deployment-, DNS-, Cloudflare-, Modell- oder Produktdateien sind nur dann nuetzlich, wenn sie das Notebook verduennt, strukturiert oder operationalisieren.
- Hilfsdateien duerfen das Notebook ergaenzen, aber nicht ersetzen.
- Modelle sollen Unterschiede als Drift markieren statt konkurrierende Wahrheiten aufzubauen.

## Praktische Folge fuer den Agenten
Wenn der Nutzer auf sein Notebook verweist, soll der Agent:
- das Notebook als Primärquelle behandeln
- andere Dateien nur als Hilfsmittel lesen
- keine alternative kanonische Parallelwelt aufbauen
- Weiterarbeit, Runbooks, Cloudflare-, Repo- und Infrastrukturplanung immer an das Notebook anbinden
