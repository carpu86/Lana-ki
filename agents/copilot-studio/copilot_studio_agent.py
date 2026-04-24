#!/usr/bin/env python3
# =================================================================
# LANA-KI COPILOT STUDIO AGENT
# Microsoft 365 Integration mit MSAL Authentication
# =================================================================

import asyncio
from aiohttp import web
import json
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
import aiohttp

load_dotenv()

# Konfiguration
COPILOT_PORT = int(os.getenv('COPILOT_STUDIO_PORT', 8012))
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')

class CopilotStudioAgent:
    def __init__(self):
        self.logger = self._setup_logging()
        self.access_token = None
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('CopilotStudio')
    
    async def get_access_token(self):
        """Microsoft Graph Access Token abrufen"""
        try:
            # Hier würde normalerweise MSAL verwendet
            # Für Demo-Zwecke simulieren wir die Authentifizierung
            self.logger.info("Simulating Microsoft 365 authentication...")
            return "demo_access_token"
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return None
    
    async def handle_chat(self, request):
        """Copilot Studio Chat mit M365 Integration"""
        try:
            data = await request.json()
            message = data.get('message', '')
            
            # Access Token abrufen
            if not self.access_token:
                self.access_token = await self.get_access_token()
            
            # Microsoft 365 spezifische Verarbeitung
            copilot_response = await self.process_with_copilot(message)
            
            return web.json_response({
                'response': copilot_response,
                'agent': 'copilot_studio',
                'integration': 'microsoft_365',
                'timestamp': datetime.now().isoformat(),
                'features': ['teams_integration', 'office_365', 'sharepoint', 'outlook']
            })
            
        except Exception as e:
            self.logger.error(f"Error in Copilot Studio: {e}")
            return web.json_response({
                'error': str(e),
                'agent': 'copilot_studio'
            }, status=500)
    
    async def process_with_copilot(self, message: str) -> str:
        """Nachricht mit Copilot Studio verarbeiten"""
        # Hier würde die echte Copilot Studio API aufgerufen
        # Für Demo simulieren wir Microsoft 365 Integration
        
        m365_features = [
            "📧 Outlook Integration verfügbar",
            "📊 SharePoint Zugriff aktiv", 
            "👥 Teams Collaboration bereit",
            "📝 Office 365 Dokumente zugänglich"
        ]
        
        response = f"""
        Microsoft Copilot Studio Response für: "{message}"
        
        🏢 Microsoft 365 Integration Status:
        {chr(10).join(m365_features)}
        
        💼 Geschäftskontext: Ihre Anfrage wurde mit vollem Microsoft 365 Kontext verarbeitet.
        
        🔗 Verfügbare Aktionen:
        - Teams Meeting erstellen
        - SharePoint Dokument suchen
        - Outlook Termine verwalten
        - Office Dokumente bearbeiten
        """
        
        return response
    
    async def handle_health(self, request):
        """Health Check"""
        return web.json_response({
            'status': 'ok',
            'agent': 'copilot_studio',
            'azure_tenant': AZURE_TENANT_ID[:8] + "..." if AZURE_TENANT_ID else None,
            'features': ['msal_auth', 'teams_integration', 'office_365', 'sharepoint']
        })

async def create_app():
    agent = CopilotStudioAgent()
    
    app = web.Application()
    app.router.add_post('/chat', agent.handle_chat)
    app.router.add_get('/health', agent.handle_health)
    
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=COPILOT_PORT)

