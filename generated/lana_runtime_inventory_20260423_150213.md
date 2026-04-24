# Lana Runtime Inventory

Erstellt: 2026-04-23 15:02:38

## Bestätigte lokale Quellen
- C:\Carpuncle Cloud\LanaApp\.env => True
- C:\Carpuncle Cloud\LanaApp\runtime_keys.env => True
- C:\Carpuncle Cloud\LanaApp\lana-master-config.env => True
- C:\Carpuncle Cloud\LanaApp\.env.clean => True
- C:\Carpuncle Cloud\LanaApp\.env.master => True

## Relevante Konfigurationswerte (maskiert oder unkritisch)
- AZURE_TENANT_ID = 9ab7fb48-3507-4326-8ebd-971d310c57fd
- AZURE_CLIENT_ID = 9050fc32-c3fe-4db5-af20-0822d1232c9d
- AZURE_SUBSCRIPTION_ID = 41ff8f43-c80b-4321-9167-2f25ac61e49a
- AZURE_REGION = west...rope
- AZURE_OPENAI_ENDPOINT = http...com/
- AZURE_AI_PROJECT_NAME = lana-ki
- AZURE_AI_FOUNDRY_PROJECT_URL = https://lana-ki-resource.services.ai.azure.com/api/projects/lana-ki
- GOOGLE_PROJECT_ID = lana-ki-cloud-core
- GOOGLE_PROJECT_NAME = lana-ki-cloud-core
- GOOGLE_USER = carp...i.de
- BRAIN_IP = 34.107.98.174
- BRAIN_TAILSCALE_IP = 100.110.207.22
- LAPTOP_IP = 100.67.27.13
- LAPTOP_TAILSCALE_IP = 100.67.27.13
- DOMAIN_NAME = lana-ki.de
- GATEWAY_URL = https://gateway.lana-ki.de
- LANA_DOMAIN_URL = https://lana-ki.de
- LANA_GATEWAY_URL = https://gateway.lana-ki.de
- LANA_API_URL = http://127.0.0.1:8010
- LANA_ORCHESTRATOR_URL = http://127.0.0.1:8024
- LANA_COMFYUI_URL = http://127.0.0.1:8188
- LANA_LMSTUDIO_URL = http://127.0.0.1:1234
- LANA_AGENT_URL = http://100.67.27.13:8100
- MASTER_AGENT_PORT = 8010
- MASTER_ORCHESTRATOR_PORT = 8024
- LANA_API_PORT = 8010
- LANA_WEBSITE_PORT = 4321
- COMFYUI_PORT = 8188
- LOCAL_MODEL = qwen2.5-7b-instruct
- LANA_BOOTSTRAP_READY = true
- LANA_MEMORY_SCOPE_MODE = per_user_per_character
- LANA_CHARACTER_STYLE_MODE = photoreal_human

## Azure CLI
`	ext
{
  "azure-cli": "2.85.0",
  "azure-cli-core": "2.85.0",
  "azure-cli-telemetry": "1.1.0",
  "extensions": {
    "account": "Unknown",
    "automation": "Unknown",
    "connectedmachine": "Unknown"
  }
}
ERROR: The command failed with an unexpected error. Here is the traceback:
ERROR: [WinError 5] Zugriff verweigert: 'C:\\Users\\carpuThomasHeckhoff\\.azure\\cliextensions\\account\\account-0.2.5.dist-info'
Traceback (most recent call last):
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\knack/cli.py", line 233, in invoke
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\azure/cli/core/commands/__init__.py", line 523, in execute
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\azure/cli/core/__init__.py", line 502, in load_command_table
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\azure/cli/core/__init__.py", line 392, in _update_command_table_from_extensions
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\azure/cli/core/extension/__init__.py", line 157, in get_metadata
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\pkginfo/wheel.py", line 16, in __init__
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\pkginfo/distribution.py", line 115, in extractMetadata
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\pkginfo/wheel.py", line 33, in read
PermissionError: [WinError 5] Zugriff verweigert: 'C:\\Users\\carpuThomasHeckhoff\\.azure\\cliextensions\\account\\account-0.2.5.dist-info'
To check existing issues, please visit: https://github.com/Azure/azure-cli/issues
ERROR: The command failed with an unexpected error. Here is the traceback:
ERROR: [WinError 5] Zugriff verweigert: 'C:\\Users\\carpuThomasHeckhoff\\.azure\\cliextensions\\account\\account-0.2.5.dist-info'
Traceback (most recent call last):
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\knack/cli.py", line 233, in invoke
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\azure/cli/core/commands/__init__.py", line 523, in execute
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\azure/cli/core/__init__.py", line 502, in load_command_table
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\azure/cli/core/__init__.py", line 392, in _update_command_table_from_extensions
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\azure/cli/core/extension/__init__.py", line 157, in get_metadata
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\pkginfo/wheel.py", line 16, in __init__
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\pkginfo/distribution.py", line 115, in extractMetadata
  File "D:\a\_work\1\s\build_scripts\windows\artifacts\cli\Lib\site-packages\pkginfo/wheel.py", line 33, in read
PermissionError: [WinError 5] Zugriff verweigert: 'C:\\Users\\carpuThomasHeckhoff\\.azure\\cliextensions\\account\\account-0.2.5.dist-info'
To check existing issues, please visit: https://github.com/Azure/azure-cli/issues
Google Cloud SDK 565.0.0
alpha 2026.04.10
beta 2026.04.10
bq 2.1.31
core 2026.04.10
gcloud-crc32c 1.0.0
gsutil 5.36
Credentialed Accounts
ACTIVE  ACCOUNT
*       carpu86de@gmail.com
        carpu@lana-ki.de

To set the active account, run:
    $ gcloud config set account `ACCOUNT`
[accessibility]
screen_reader = False
[core]
account = carpu86de@gmail.com
disable_usage_reporting = False
project = lana-ki-cloud-core

Your active configuration is: [default]
[environment: untagged] Read more to tag: g.co/cloud/project-env-tag.
PROJECT_ID                      NAME                      PROJECT_NUMBER  ENVIRONMENT
cs-host-d5bb447f7b1e44088c8147  Cloud Setup Host Project  395247151407
google-mpf-mq7v1bg82uyx         Proof of Concept-mp       768464006746
lana-ki-cloud-core              Carpuncle Cloud Lana-ki   516487041696
lana-ki-unified-20260411        Lana-KI Unified Platform  776513340613
watchful-nature-8kw4x                                     421156224173
NAME               ZONE            MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
lana-master-brain  europe-west3-c  e2-standard-2               10.156.0.2   34.107.98.174  RUNNING
`	ext
% Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
HTTP/1.1 200 OK
Date: Thu, 23 Apr 2026 13:02:36 GMT
Content-Type: text/html
Connection: keep-alive
Nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
last-modified: Wed, 22 Apr 2026 12:44:48 GMT
Server: cloudflare
vary: Accept-Encoding
Report-To: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=%2BX6YvHuSzBvyDrDq%2BydDics5PL71MW%2FL2t1swPXZuqTf2z4HCmfHaX25LxOY8vlNzqiJuL8QpRXlK3R13fRu3Zm6Bq5WwBvvuamo8ZaSOoyutoeomPcpAVSSIwUG"}]}
cf-cache-status: DYNAMIC
CF-RAY: 9f0d103eebca7a98-FRA
alt-svc: h3=":443"; ma=86400

  0      0   0      0   0      0      0      0           00:01              0
  0      0   0      0   0      0      0      0           00:01              0
  0      0   0      0   0      0      0      0           00:01              0
  0      0   0      0   0      0      0      0           00:01              0
% Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100     60 100     60   0      0     93      0                              0
100     60 100     60   0      0     93      0                              0
100     60 100     60   0      0     93      0                              0
{"ok":true,"service":"lana-api","host":"laptop","port":8010}
% Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100    667 100    667   0      0  75649      0                              0
100    667 100    667   0      0  74658      0                              0
100    667 100    667   0      0  73677      0                              0
{"system": {"os": "win32", "ram_total": 17062543360, "ram_free": 3161939968, "comfyui_version": "0.19.0", "required_frontend_version": "1.42.10", "installed_templates_version": "0.9.47", "required_templates_version": "0.9.47", "python_version": "3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]", "pytorch_version": "2.11.0+cu126", "embedded_python": true, "argv": ["main.py", "--listen", "127.0.0.1", "--port", "8188", "--lowvram"]}, "devices": [{"name": "cuda:0 NVIDIA GeForce RTX 4060 : cudaMallocAsync", "type": "cuda", "index": 0, "vram_total": 8585216000, "vram_free": 7452229632, "torch_vram_total": 0, "torch_vram_free": 0}]}
% Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0           00:01              0
  0      0   0      0   0      0      0      0           00:02              0
curl: (7) Failed to connect to 127.0.0.1 port 1234 after 2030 ms: Could not connect to server
- Copilot Studio Lizenz: vom Nutzer bestätigt
- Azure-Konto: vom Nutzer als ungenutzt/verfügbar bestätigt
- GCloud hostet VM: vom Nutzer bestätigt
