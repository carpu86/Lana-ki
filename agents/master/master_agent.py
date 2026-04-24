#!/usr/bin/env python3
# =================================================================
# LANA-KI MASTER ORCHESTRATOR AGENT
# Intelligente Weiterleitung an spezialisierte Agenten
# =================================================================

import asyncio
import aiohttp
from aiohttp import web
import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Konfiguration
MASTER_PORT = int(os.getenv('MASTER_AGENT_PORT', 8010))
AGENTS = {
    'gemini_enterprise': {
        'url': f"http://127.0.0.1:{os.getenv('GEMINI_ENTERPRISE_PORT', 8011)}",
        'description': 'Erweiterte KI-Funktionen mit Vertex AI',
        'keywords': ['enterprise', 'vertex', 'advanced', 'business']
    },
    'copilot_studio': {
        'url': f"http://127.0.0.1:{os.getenv('COPILOT_STUDIO_PORT', 8012)}",
        'description': 'Microsoft 365 Integration mit MSAL',
        'keywords': ['microsoft', 'office', 'm365', 'copilot', 'teams']
    },
    'gemini_gems': {
        'url': f"http://127.0.0.1:{os.getenv('GEMINI_GEMS_PORT', 8013)}",
        'description': 'Spezialisierte KI-Persönlichkeiten',
        'keywords': ['personality', 'character', 'roleplay', 'gems']
    }
}

class MasterOrchestrator:
    def __init__(self):
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('MasterOrchestrator')
    
    def select_agent(self, message: str) -> str:
        """Intelligente Agent-Auswahl basierend auf Nachrichteninhalt"""
        message_lower = message.lower()
        
        # Scoring-System für Agent-Auswahl
        scores = {}
        for agent_name, agent_info in AGENTS.items():
            score = 0
            for keyword in agent_info['keywords']:
                if keyword in message_lower:
                    score += 1
            scores[agent_name] = score
        
        # Besten Agent auswählen
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # Fallback: Gemini Enterprise für allgemeine Anfragen
        return 'gemini_enterprise'
    
    async def forward_to_agent(self, agent_name: str, message: str) -> dict:
        """Nachricht an spezialisierten Agent weiterleiten"""
        try:
            agent_url = AGENTS[agent_name]['url']
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{agent_url}/chat",
                    json={'message': message},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {
                            'error': f'Agent {agent_name} returned status {response.status}',
                            'agent': agent_name
                        }
        except Exception as e:
            self.logger.error(f"Error forwarding to {agent_name}: {e}")
            return {
                'error': f'Failed to reach agent {agent_name}: {str(e)}',
                'agent': agent_name
            }
    
    async def handle_chat(self, request):
        """Hauptendpoint für Chat-Anfragen"""
        try:
            data = await request.json()
            message = data.get('message', '')
            
            if not message:
                return web.json_response({'error': 'No message provided'}, status=400)
            
            # Agent auswählen
            selected_agent = self.select_agent(message)
            self.logger.info(f"Selected agent: {selected_agent} for message: {message[:50]}...")
            
            # An Agent weiterleiten
            response = await self.forward_to_agent(selected_agent, message)
            response['selected_agent'] = selected_agent
            response['timestamp'] = datetime.now().isoformat()
            
            return web.json_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in handle_chat: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_status(self, request):
        """Status-Endpoint"""
        agent_status = {}
        
        for agent_name, agent_info in AGENTS.items():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{agent_info['url']}/health",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        agent_status[agent_name] = {
                            'status': 'online' if response.status == 200 else 'error',
                            'description': agent_info['description']
                        }
            except:
                agent_status[agent_name] = {
                    'status': 'offline',
                    'description': agent_info['description']
                }
        
        return web.json_response({
            'master_orchestrator': 'online',
            'agents': agent_status,
            'timestamp': datetime.now().isoformat()
        })

async def create_app():
    orchestrator = MasterOrchestrator()
    
    app = web.Application()
    app.router.add_post('/chat', orchestrator.handle_chat)
    app.router.add_get('/status', orchestrator.handle_status)
    app.router.add_get('/health', lambda r: web.json_response({'status': 'ok'}))
    
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=MASTER_PORT)

