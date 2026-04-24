#!/usr/bin/env python3
# =================================================================
# GEMINI API TESTER - LANA-KI INFRASTRUKTUR
# =================================================================

import os
import google.generativeai as genai
from datetime import datetime

# Konfiguration
GEMINI_API_KEY = "AIzaSyCMwmUjPI26VLkBwtFWZiT4TXm6NFVBYiA"
PROJECT_ID = "lana-ki-cloud-core"

def test_gemini_api():
    print("🧪 TESTE GEMINI API INTEGRATION...")
    print("=" * 50)
    
    try:
        # API konfigurieren
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Verfügbare Modelle auflisten
        print("\n📋 Verfügbare Modelle:")
        models = list(genai.list_models())
        for model in models[:5]:  # Erste 5 Modelle
            print(f"  • {model.name}")
        
        # Test-Anfrage
        print("\n🔬 Führe Test-Anfrage durch...")
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        test_prompt = f"Hallo! Ich bin Lana-KI und teste die Gemini API Integration. Aktuelle Zeit: {datetime.now()}"
        
        response = model.generate_content(test_prompt)
        
        print("✅ GEMINI API TEST ERFOLGREICH!")
        print(f"Antwort: {response.text[:200]}...")
        
        if hasattr(response, 'usage_metadata'):
            print(f"Token verwendet: {response.usage_metadata.total_token_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ GEMINI API TEST FEHLGESCHLAGEN: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    exit(0 if success else 1)
