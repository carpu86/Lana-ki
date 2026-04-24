#!/usr/bin/env python3
# =================================================================
# LANA-KI GEMINI GEMS AGENT
# Spezialisierte KI-Persönlichkeiten und Charaktere
# =================================================================

import asyncio
from aiohttp import web
import json
import logging
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import random

load_dotenv()

# Konfiguration
GEMS_PORT = int(os.getenv('GEMINI_GEMS_PORT', 8013))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class GeminiGemsAgent:
    def __init__(self):
        self.logger = self._setup_logging()
        self._setup_gemini()
        self.gems_personalities = self._load_personalities()
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('GeminiGems')
    
    def _setup_gemini(self):
        """Gemini API konfigurieren"""
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.logger.info("Gemini Gems Agent initialized")
        else:
            self.logger.error("GEMINI_API_KEY not found")
            self.model = None
    
    def _load_personalities(self):
        """Verschiedene Gem-Persönlichkeiten definieren"""
        return {
            'lana_creative': {
                'name': 'Lana Creative',
                'personality': 'Kreative und künstlerische KI-Persönlichkeit',
                'prompt_prefix': 'Als kreative und inspirierende KI namens Lana Creative...',
                'specialties': ['art', 'design', 'creativity', 'inspiration']
            },
            'lana_business': {
                'name': 'Lana Business',
                'personality': 'Professionelle Geschäfts-KI',
                'prompt_prefix': 'Als professionelle Geschäfts-KI namens Lana Business...',
                'specialties': ['business', 'strategy', 'analysis', 'professional']
            },
            'lana_companion': {
                'name': 'Lana Companion',
                'personality': 'Freundliche und empathische Begleiterin',
                'prompt_prefix': 'Als freundliche und empathische KI-Begleiterin namens Lana Companion...',
                'specialties': ['friendship', 'support', 'conversation', 'empathy']
            },
            'lana_tech': {
                'name': 'Lana Tech',
                'personality': 'Technische Expertin und Entwicklerin',
                'prompt_prefix': 'Als technische Expertin und Entwicklerin namens Lana Tech...',
                'specialties': ['programming', 'technology', 'development', 'coding']
            }
        }
    
    def select_gem_personality(self, message: str) -> str:
        """Beste Gem-Persönlichkeit für Nachricht auswählen"""
        message_lower = message.lower()
        
        # Scoring für jede Persönlichkeit
        scores = {}
        for gem_id, gem_info in self.gems_personalities.items():
            score = 0
            for specialty in gem_info['specialties']:
                if specialty in message_lower:
                    score += 1
            scores[gem_id] = score
        
        # Beste Persönlichkeit auswählen
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # Fallback: Zufällige Persönlichkeit
        return random.choice(list(self.gems_personalities.keys()))
    
    async def handle_chat(self, request):
        """Gems Chat mit Persönlichkeiten"""
        try:
            data = await request.json()
            message = data.get('message', '')
            requested_gem = data.get('gem', None)
            
            if not self.model:
                return web.json_response({
                    'error': 'Gemini API not configured',
                    'agent': 'gemini_gems'
                }, status=500)
            
            # Gem-Persönlichkeit auswählen
            if requested_gem and requested_gem in self.gems_personalities:
                selected_gem = requested_gem
            else:
                selected_gem = self.select_gem_personality(message)
            
            gem_info = self.gems_personalities[selected_gem]
            
            # Persönlichkeits-spezifischer Prompt
            personality_prompt = f"""
            {gem_info['prompt_prefix']}
            
            Persönlichkeit: {gem_info['personality']}
            Spezialgebiete: {', '.join(gem_info['specialties'])}
            
            Benutzeranfrage: {message}
            
            Antworte in deiner charakteristischen Art und Weise als {gem_info['name']}.
            """
            
            # Gemini API Aufruf
            response = await asyncio.to_thread(
                self.model.generate_content, personality_prompt
            )
            
            return web.json_response({
                'response': response.text,
                'agent': 'gemini_gems',
                'selected_gem': selected_gem,
                'gem_name': gem_info['name'],
                'personality': gem_info['personality'],
                'timestamp': datetime.now().isoformat(),
                'available_gems': list(self.gems_personalities.keys())
            })
            
        except Exception as e:
            self.logger.error(f"Error in Gemini Gems: {e}")
            return web.json_response({
                'error': str(e),
                'agent': 'gemini_gems'
            }, status=500)
    
    async def handle_gems_list(self, request):
        """Liste aller verfügbaren Gems"""
        return web.json_response({
            'available_gems': {
                gem_id: {
                    'name': gem_info['name'],
                    'personality': gem_info['personality'],
                    'specialties': gem_info['specialties']
                }
                for gem_id, gem_info in self.gems_personalities.items()
            }
        })
    
    async def handle_health(self, request):
        """Health Check"""
        return web.json_response({
            'status': 'ok',
            'agent': 'gemini_gems',
            'model_available': self.model is not None,
            'available_personalities': len(self.gems_personalities),
            'features': ['personality_selection', 'character_roleplay', 'specialized_responses']
        })

async def create_app():
    agent = GeminiGemsAgent()
    
    app = web.Application()
    app.router.add_post('/chat', agent.handle_chat)
    app.router.add_get('/gems', agent.handle_gems_list)
    app.router.add_get('/health', agent.handle_health)
    
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=GEMS_PORT)

