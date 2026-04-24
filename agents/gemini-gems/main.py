#!/usr/bin/env python3
# =================================================================
# LANA-KI GEMINI GEMS AGENT
# Spezialisiert auf Code-Generierung und strukturierte Aufgaben
# =================================================================

import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import uvicorn

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lana-KI Gemini Gems Agent", version="2.0.0")

# Gemini Konfiguration
GEMINI_API_KEY = "AIzaSyCMwmUjPI26VLkBwtFWZiT4TXm6NFVBYiA"
GEMINI_PROJECT_ID = "lana-ki-cloud-core"

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable required")

genai.configure(api_key=GEMINI_API_KEY)

class GemsRequest(BaseModel):
    task: str
    code_language: Optional[str] = "python"
    framework: Optional[str] = None
    complexity: str = "medium"  # simple, medium, complex
    include_tests: bool = False
    include_docs: bool = True

class GemsResponse(BaseModel):
    code: str
    explanation: str
    tests: Optional[str] = None
    documentation: str
    language: str
    framework_used: Optional[str] = None

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "agent": "gemini-gems", 
        "version": "2.0.0",
        "specialization": "code_generation",
        "supported_languages": ["python", "javascript", "powershell", "bash", "sql"]
    }

@app.post("/generate", response_model=GemsResponse)
async def generate_code(request: GemsRequest):
    try:
        # Spezialisierter Prompt für Code-Generierung
        system_prompt = f"""
Du bist ein Experte für {request.code_language} Entwicklung.
Aufgabe: {request.task}
Sprache: {request.code_language}
Framework: {request.framework or 'Standard'}
Komplexität: {request.complexity}

Erstelle:
1. Sauberen, produktionsreifen Code
2. Klare Erklärung der Implementierung
3. {'Unit Tests' if request.include_tests else 'Keine Tests nötig'}
4. {'Ausführliche Dokumentation' if request.include_docs else 'Kurze Dokumentation'}

Fokus auf: Lesbarkeit, Wartbarkeit, Best Practices
"""
        
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(
            system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Niedrigere Temperatur für Code
                max_output_tokens=4096,
            )
        )
        
        # Parse Response (vereinfacht - kann erweitert werden)
        response_text = response.text
        
        # Extrahiere Code-Blöcke (vereinfachte Logik)
        code_start = response_text.find("`")
        code_end = response_text.rfind("`")
        
        if code_start != -1 and code_end != -1 and code_start < code_end:
            code = response_text[code_start+3:code_end].strip()
            # Entferne Sprach-Identifier
            if code.startswith(request.code_language):
                code = code[len(request.code_language):].strip()
        else:
            code = response_text
        
        return GemsResponse(
            code=code,
            explanation=response_text,
            tests=None,  # Kann erweitert werden
            documentation=response_text,
            language=request.code_language,
            framework_used=request.framework
        )
        
    except Exception as e:
        logger.error(f"Gemini Gems error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code generation error: {str(e)}")

@app.post("/optimize")
async def optimize_code(code: str, language: str = "python"):
    """Optimiert bestehenden Code"""
    try:
        prompt = f"""
Optimiere diesen {language} Code:

`{language}
{code}
`

Fokus auf:
- Performance
- Lesbarkeit  
- Best Practices
- Fehlerbehandlung
- Dokumentation

Gib den optimierten Code mit Erklärung der Verbesserungen zurück.
"""
        
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        
        return {
            "optimized_code": response.text,
            "language": language,
            "optimization_notes": "Code wurde für Performance und Lesbarkeit optimiert"
        }
        
    except Exception as e:
        logger.error(f"Code optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8022)
