# Box / Hetzner Storage / FRITZ!Box Integration

Stand: 2026-05-16

## Root Cause

Box.com, SharePoint/OneDrive, ZIP-Archive und FRITZ!Box/NAS sind aktuell vermischte Austausch-, Notizbuch- und Backup-Ebenen. Die FRITZ!Box ist kein nativer Box.com- oder SharePoint-Cloud-Connector. Sie ist als VPN-/NAS-Zugang zu behandeln.

## Belegter Ist-Stand

- FRITZ!Box-VPN Host `carpu`: `192.168.178.201`
- FRITZ!Box-VPN Host `u585979`: `192.168.178.202`
- SharePoint-Ziel bestaetigt: `carpu-my.sharepoint.com/personal/carpu_lana-ki_de`
- SharePoint-Bibliothek: `Dokumente`
- SharePoint-Ordner: `Lana_Notizbuch`
- Box.com: als Notizbuch-/Austauschziel gewuenscht, aber in dieser Session kein Box-Connector aktiv belegt.
- Hetzner Storage/WebDAV: als Option genannt, konkrete Zugangsdaten/Live-Test nicht dokumentiert.

## Entscheidung

- Fuer NAS-nahe Dateiablage: Hetzner Storage/WebDAV bevorzugen, falls der Zugang live funktioniert.
- Fuer Notizbuch-/Collaboration-Ebene: SharePoint `Lana_Notizbuch` ist bereits eingerichtet.
- Fuer Box.com: nur als zusaetzliche Sync-/Notizbuch-Kopie ueber Box Drive oder rclone auf Node B/Node D einbinden, nicht direkt ueber FRITZ!Box.

## Sichere Zielstruktur

- Master-Doku lokal: `C:\Carpuncle Cloud\Lana KI\docs`
- SharePoint-Kopie: `Dokumente/Lana_Notizbuch`
- NAS/Cold Storage: FRITZ!Box nur via VPN/offline-first
- Box.com: nur bereinigte Markdown-/PUML-/PDF-Artefakte, keine Roh-ZIPs, keine `.env`, keine Logs mit Tokens
- Hetzner Storage/WebDAV: Backup-/Mirror-Ziel fuer bereinigte Artefakte und Archive nach Secret-Pruefung

## Nicht synchronisieren

- `.env`
- Vaults
- private Keys
- OAuth-/Tunnel-/API-Tokens
- Roh-ZIPs mit unbekanntem Inhalt
- Logs mit Tokens oder Credentials
- Service-Account-JSONs

## Testblock

Vor jeder echten Sync-Aktion:

1. Quelle auf Secret-Muster pruefen.
2. Zielpfad und Besitzrechte pruefen.
3. Dry-run ausfuehren.
4. Nur bereinigte Artefakte synchronisieren.
5. Zielinhalt gegenlesen.

## Offene Punkte

- Box.com Zugriffsmethode festlegen: Box Drive auf Windows oder rclone auf Debian.
- Hetzner Storage/WebDAV live pruefen.
- FRITZ!Box-VPN fuer `carpu` und `u585979` ohne Credentials dokumentieren.
- Sync-Skript erst nach Secret-Rotation aktivieren.
