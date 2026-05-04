# 🧰 LANA‑KI – Restore Kit (Node B als Primär-Vault)

**Dokumenttyp:** Betriebs- und Wiederherstellungsleitfaden  
**Scope:** Identity Pack, State Pack, Restore Pack  
**Secrets:** ❌ keine Klartext‑Secrets  
**Status:** baseline

---

## 1. Ziel

Lana muss bei Node‑Ausfall verletzt sein dürfen, aber nicht sterben:

- Identität bleibt erhalten
- Recovery‑Wissen bleibt erhalten
- Steuerfähigkeit bleibt erhalten

---

## 2. Primärer Speicherort

`C:\Carpuncle Cloud\LanaVault`

Laptop (Node D) ist **kein** primärer Memory‑Knoten.

---

## 3. Soll-Struktur

```text
C:\Carpuncle Cloud\LanaVault\
  identity\
    LANA_IDENTITY.md
    LANA_CONSTITUTION.md
    NODE_ROLES.md

  state\
    topology-state.json
    service-registry.json
    last-known-good.json
    port-registry.json

  memory\
    memory-index.json
    girl-memory\
    system-memory\
    project-memory\

  secrets-ref\
    env.inventory.sanitized.md
    secret-map.json
    rotation-ledger.sanitized.md

  restore\
    RESTORE_NEW_WINDOWS.md
    RESTORE_NEW_CLOUD_SERVER.md
    RESTORE_NODE_D_MONITOR.md
    install-node-b.ps1
    verify-node-b.ps1

  audit\
    audit-ledger.md
    incident-ledger.md

  backups\
    env\
    configs\
    service-manifests\
```

---

## 4. Restore-Checkliste (Node B, Windows neu)

1. Laufwerke prüfen  
2. GPU prüfen  
3. Python/Node/Git prüfen  
4. `C:\Carpuncle Cloud` prüfen  
5. Restore Kit prüfen  
6. Secrets nur auf Vorhandensein prüfen (kein Klartext)  
7. Services wiederherstellen  
8. Worker starten  
9. Health prüfen  
10. Fehlende Bausteine melden + Audit schreiben

---

## 5. Secret-Policy

Lana darf Secret‑Namen, Speicherorte und Rotationsstatus verwalten, aber nie Klartext‑Werte ausgeben oder loggen.

Verbotene Ziele für Klartext‑Secrets:

- Chat
- Logs
- GitHub
- Notion
- Jira
- Slack
- externe Recherche-/Analyse-Tools
