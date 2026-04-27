# ☁️ LANA‑KI – Azure Setup

Diese Datei dokumentiert das **verbindliche Azure‑Setup** für das LANA‑KI‑Projekt.

Quelle der Wahrheit ist **ausschließlich die Azure CLI (z)** –
nicht das Azure‑Portal.

---

## 🏢 Azure Tenant

**Name:** Carpuncle.ai  
**Tenant ID:** 9ab7fb48-3507-4326-8ebd-971d310c57fd

---

## 📦 Azure Subscriptions (CLI-Wahrheit)

| Name | Subscription ID | Status | Default |
|------|------------------|--------|---------|
| carpuncle.de | 41ff8f43-c80b-4321-9167-2f25ac61e49a | Enabled | ✅ |
| Lana | 7ae249e7-f211-4cd1-9b8e-8210e75dc7e1 | Enabled | ❌ |
| carpu | ef2a2e1d-e0f0-4abb-a55f-3abbbcbee1df | Enabled | ❌ |

---

## 🎯 Verbindliche Subscription für LANA‑KI

**carpuncle.de**  
41ff8f43-c80b-4321-9167-2f25ac61e49a

---

## 🔑 Azure CLI Pflichtbefehle

`powershell
az login
az account set --subscription 41ff8f43-c80b-4321-9167-2f25ac61e49a
az account show --output table