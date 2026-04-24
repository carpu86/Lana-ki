import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Drive API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# OAuth Credentials aus deiner .env
CLIENT_ID = "1342008665-o8b54aabeibr55tbgonk68iam9jt9kn1.apps.googleusercontent.com"
CLIENT_SECRET = "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"

def setup_google_drive():
    """Setup Google Drive API"""
    creds = None
    token_path = "token.json"
    
    # Lade existierende Credentials
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Falls keine gültigen Credentials, starte OAuth Flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Erstelle credentials.json für OAuth
            credentials_info = {
                "installed": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            with open("credentials.json", "w") as f:
                json.dump(credentials_info, f)
            
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Speichere Credentials
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def list_drive_files():
    """Liste Google Drive Dateien"""
    try:
        service = setup_google_drive()
        
        # Hole erste 10 Dateien
        results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])
        
        if not items:
            print('Keine Dateien gefunden.')
            return
        
        print('📁 GOOGLE DRIVE DATEIEN:')
        for item in items:
            print(f"  • {item['name']} ({item['mimeType']})")
            
    except Exception as e:
        print(f"Google Drive Fehler: {e}")

def upload_to_drive(file_path, folder_name="Lana-KI"):
    """Upload Datei zu Google Drive"""
    try:
        service = setup_google_drive()
        
        # Erstelle Lana-KI Ordner falls nicht vorhanden
        folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        folders = service.files().list(q=folder_query).execute().get('files', [])
        
        if not folders:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=folder_metadata).execute()
            folder_id = folder.get('id')
            print(f"📁 Ordner '{folder_name}' erstellt")
        else:
            folder_id = folders[0].get('id')
        
        # Upload Datei
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(file_path)
        
        file = service.files().create(body=file_metadata, media_body=media).execute()
        print(f"✅ Datei hochgeladen: {file.get('name')}")
        
    except Exception as e:
        print(f"Upload Fehler: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🔗 GOOGLE DRIVE INTEGRATION")
        print("Verwendung:")
        print("  python google_drive.py list")
        print("  python google_drive.py upload <datei_pfad>")
    elif sys.argv[1] == "list":
        list_drive_files()
    elif sys.argv[1] == "upload" and len(sys.argv) > 2:
        upload_to_drive(sys.argv[2])
    else:
        print("Unbekannter Befehl")
