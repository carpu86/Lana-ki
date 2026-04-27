# ☁️ LANA-KI – Azure Setup

Diese Datei dokumentiert das verbindliche Azure-Setup für das LANA-KI-Projekt.

Quelle der Wahrheit ist ausschließlich die Azure CLI `az`.

---

## 🏢 Azure Tenant

**Name:** Carpuncle.ai  
**Tenant ID:** `9ab7fb48-3507-4326-8ebd-971d310c57fd`

Alle produktiven Azure-Ressourcen für LANA-KI befinden sich in diesem Tenant.

---

## 📦 Azure Subscriptions

| Name | Subscription ID | Status | Default |
|------|------------------|--------|---------|
| carpuncle.de | `41ff8f43-c80b-4321-9167-2f25ac61e49a` | Enabled | ✅ |
| Lana | `7ae249e7-f211-4cd1-9b8e-8210e75dc7e1` | Enabled | ❌ |
| carpu | `ef2a2e1d-e0f0-4abb-a55f-3abbbcbee1df` | Enabled | ❌ |

---

## 🎯 Verbindliche Subscription für LANA-KI

**Name:** carpuncle.de  
**Subscription ID:** `41ff8f43-c80b-4321-9167-2f25ac61e49a`

Diese Subscription ist verbindlich für alle Azure-Ressourcen von LANA-KI.

---

## 🔑 Azure CLI Pflichtbefehle

    az login
    az account set --subscription 41ff8f43-c80b-4321-9167-2f25ac61e49a
    az account show --output table

---

## ✅ Erwarteter CLI-Kontext

| Feld | Wert |
|------|------|
| TenantDisplayName | Carpuncle.ai |
| TenantDefaultDomain | lana-ki.de |
| TenantId | `9ab7fb48-3507-4326-8ebd-971d310c57fd` |
| Subscription | carpuncle.de |
| SubscriptionId | `41ff8f43-c80b-4321-9167-2f25ac61e49a` |

---

## 🛡️ Sicherheitsregel

Secrets, API-Keys und Tokens werden nicht in dieses Repository geschrieben.  
Credential-Verwaltung erfolgt über 1Password CLI oder lokale `.env` außerhalb öffentlicher Commits.