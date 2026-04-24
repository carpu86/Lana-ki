import requests
import json
import sys
from msal import ConfidentialClientApplication

# Azure App Credentials aus deiner .env
TENANT_ID = "9ab7fb48-3507-4326-8ebd-971d310c57fd"
CLIENT_ID = "3cf6df92-2745-4f6f-bbcf-19b59bcdb62a"  # Aus MS365_CONFIG_TOKEN
SHAREPOINT_SITE = "carpuncle.sharepoint.com"

def get_access_token():
    """Hole Azure Access Token für SharePoint"""
    try:
        # Verwende Device Code Flow für einfache Authentifizierung
        authority = f"https://login.microsoftonline.com/{TENANT_ID}"
        scopes = ["https://graph.microsoft.com/.default"]
        
        # Erstelle MSAL App
        app = ConfidentialClientApplication(
            CLIENT_ID,
            authority=authority
        )
        
        # Device Code Flow
        flow = app.initiate_device_flow(scopes=scopes)
        
        if "user_code" not in flow:
            raise ValueError("Device Flow konnte nicht gestartet werden")
        
        print(f"🔐 AZURE LOGIN:")
        print(f"Gehe zu: {flow['verification_uri']}")
        print(f"Code eingeben: {flow['user_code']}")
        input("Drücke Enter wenn Login abgeschlossen...")
        
        result = app.acquire_token_by_device_flow(flow)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            print(f"Login Fehler: {result.get('error_description')}")
            return None
            
    except Exception as e:
        print(f"Token Fehler: {e}")
        return None

def list_onedrive_files():
    """Liste OneDrive Dateien"""
    token = get_access_token()
    if not token:
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Hole OneDrive Dateien
        url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            files = response.json().get('value', [])
            
            print("📁 ONEDRIVE DATEIEN:")
            for file in files[:10]:  # Erste 10 Dateien
                print(f"  • {file['name']} ({file.get('size', 0)} bytes)")
        else:
            print(f"OneDrive Fehler: {response.status_code}")
            
    except Exception as e:
        print(f"OneDrive Fehler: {e}")

def upload_to_onedrive(file_path):
    """Upload Datei zu OneDrive"""
    token = get_access_token()
    if not token:
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream"
        }
        
        filename = os.path.basename(file_path)
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filename}:/content"
        
        with open(file_path, 'rb') as f:
            response = requests.put(url, headers=headers, data=f)
        
        if response.status_code in [200, 201]:
            print(f"✅ Datei hochgeladen: {filename}")
        else:
            print(f"Upload Fehler: {response.status_code}")
            
    except Exception as e:
        print(f"Upload Fehler: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🔗 SHAREPOINT/ONEDRIVE INTEGRATION")
        print("Verwendung:")
        print("  python sharepoint.py list")
        print("  python sharepoint.py upload <datei_pfad>")
    elif sys.argv[1] == "list":
        list_onedrive_files()
    elif sys.argv[1] == "upload" and len(sys.argv) > 2:
        upload_to_onedrive(sys.argv[2])
    else:
        print("Unbekannter Befehl")
