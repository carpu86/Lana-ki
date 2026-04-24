#!/usr/bin/env python3
# =================================================================
# LANA-KI TELEGRAM BOT
# Intelligente Weiterleitung an Multi-Agent System
# =================================================================

import asyncio
import aiohttp
from aiohttp import web
import json
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Konfiguration
TELEGRAM_PORT = int(os.getenv('TELEGRAM_BOT_PORT', 8014))
MASTER_AGENT_URL = f"http://127.0.0.1:{os.getenv('MASTER_AGENT_PORT', 8010)}"

class LanaTelegramBot:
    def __init__(self):
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('LanaTelegramBot')
    
    async def forward_to_master(self, message: str) -> dict:
        """Nachricht an Master Orchestrator weiterleiten"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{MASTER_AGENT_URL}/chat",
                    json={'message': message},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {
                            'error': f'Master agent returned status {response.status}',
                            'fallback_response': 'Entschuldigung, ich bin gerade nicht verfügbar. Versuche es später nochmal.'
                        }
        except Exception as e:
            self.logger.error(f"Error forwarding to master: {e}")
            return {
                'error': str(e),
                'fallback_response': 'Es gab ein technisches Problem. Bitte versuche es später nochmal.'
            }
    
    async def handle_telegram_webhook(self, request):
        """Telegram Webhook Handler"""
        try:
            data = await request.json()
            
            # Telegram Message extrahieren
            if 'message' in data and 'text' in data['message']:
                user_message = data['message']['text']
                chat_id = data['message']['chat']['id']
                user_name = data['message']['from'].get('first_name', 'User')
                
                self.logger.info(f"Received message from {user_name}: {user_message}")
                
                # An Master Agent weiterleiten
                response = await self.forward_to_master(user_message)
                
                # Telegram Response formatieren
                if 'error' in response:
                    bot_response = response.get('fallback_response', 'Entschuldigung, es gab einen Fehler.')
                else:
                    bot_response = response.get('response', 'Keine Antwort erhalten.')
                    selected_agent = response.get('selected_agent', 'unknown')
                    
                    # Agent-Info hinzufügen
                    agent_names = {
                        'gemini_enterprise': '🏢 Lana Enterprise',
                        'copilot_studio': '💼 Lana Copilot',
                        'gemini_gems': '💎 Lana Gems'
                    }
                    
                    agent_display = agent_names.get(selected_agent, selected_agent)
                    bot_response = f"{bot_response}\n\n_Beantwortet von: {agent_display}_"
                
                # Hier würde normalerweise die Telegram Bot API aufgerufen
                # Für Demo loggen wir die Response
                self.logger.info(f"Sending to {chat_id}: {bot_response[:100]}...")
                
                return web.json_response({'status': 'ok'})
            
            return web.json_response({'status': 'ignored'})
            
        except Exception as e:
            self.logger.error(f"Error in telegram webhook: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_send_message(self, request):
        """Direkter Message-Send Endpoint (für Tests)"""
        try:
            data = await request.json()
            message = data.get('message', '')
            
            if not message:
                return web.json_response({'error': 'No message provided'}, status=400)
            
            # An Master Agent weiterleiten
            response = await self.forward_to_master(message)
            
            return web.json_response({
                'telegram_bot_response': response,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error in send_message: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_health(self, request):
        """Health Check"""
        # Master Agent Status prüfen
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{MASTER_AGENT_URL}/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    master_status = 'online' if response.status == 200 else 'error'
        except:
            master_status = 'offline'
        
        return web.json_response({
            'status': 'ok',
            'agent': 'telegram_bot',
            'master_agent_status': master_status,
            'features': ['webhook_handler', 'multi_agent_routing', 'telegram_integration']
        })

async def create_app():
    bot = LanaTelegramBot()
    
    app = web.Application()
    app.router.add_post('/webhook', bot.handle_telegram_webhook)
    app.router.add_post('/send', bot.handle_send_message)
    app.router.add_get('/health', bot.handle_health)
    
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=TELEGRAM_PORT)

