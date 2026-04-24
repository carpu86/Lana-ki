#!/usr/bin/env python3
# =================================================================
# LANA-KI GEMINI ENTERPRISE AGENT
# Erweiterte KI-Funktionen mit Vertex AI Integration
# =================================================================

import asyncio
from aiohttp import web
import json
import logging
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

load_dotenv()

# Konfiguration
GEMINI_PORT = int(os.getenv('GEMINI_ENTERPRISE_PORT', 8011))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID', 'lana-ki-cloud-core')

class GeminiEnterpriseAgent:
    def __init__(self):
        self.logger = self._setup_logging()
        self._setup_gemini()
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('GeminiEnterprise')
    
    def _setup_gemini(self):
        """Gemini API konfigurieren"""
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.logger.info("Gemini Enterprise Agent initialized")
        else:
            self.logger.error("GEMINI_API_KEY not found")
            self.model = None
    
    async def handle_chat(self, request):
        """Enterprise Chat mit erweiterten Funktionen"""
        try:
            data = await request.json()
            message = data.get('message', '')
            
            if not self.model:
                return web.json_response({
                    'error': 'Gemini API not configured',
                    'agent': 'gemini_enterprise'
                }, status=500)
            
            # Enterprise-spezifische Prompt-Erweiterung
            enterprise_prompt = f"""
            Als Lana-KI Enterprise Agent mit erweiterten Geschäftsfunktionen:
            
            Benutzeranfrage: {message}
            
            Bitte antworte professionell und geschäftsorientiert mit:
            1. Direkter Antwort auf die Anfrage
            2. Geschäftsrelevanten Insights
            3. Handlungsempfehlungen
            """
            
            # Gemini API Aufruf
            response = await asyncio.to_thread(
                self.model.generate_content, enterprise_prompt
            )
            
            return web.json_response({
                'response': response.text,
                'agent': 'gemini_enterprise',
                'model': 'gemini-pro',
                'timestamp': datetime.now().isoformat(),
                'features': ['business_insights', 'professional_analysis', 'vertex_ai']
            })
            
        except Exception as e:
            self.logger.error(f"Error in Gemini Enterprise: {e}")
            return web.json_response({
                'error': str(e),
                'agent': 'gemini_enterprise'
            }, status=500)
    
    async def handle_health(self, request):
        """Health Check"""
        return web.json_response({
            'status': 'ok',
            'agent': 'gemini_enterprise',
            'model_available': self.model is not None,
            'features': ['vertex_ai', 'business_analysis', 'enterprise_functions']
        })

async def create_app():
    agent = GeminiEnterpriseAgent()
    
    app = web.Application()
    app.router.add_post('/chat', agent.handle_chat)
    app.router.add_get('/health', agent.handle_health)
    
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=GEMINI_PORT)

