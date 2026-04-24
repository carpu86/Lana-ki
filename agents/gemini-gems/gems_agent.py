#!/usr/bin/env python3
# Gemini Gems Agent für Lana-KI Platform

import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import uvicorn

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lana-KI Gemini Gems Agent", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class GemRequest(BaseModel):
    message: str
    gem_type: str = "creative"
    style: str = "friendly"
    language: str = "de"

class GemResponse(BaseModel):
    response: str
    gem_type: str
    style: str
    model: str = "gemini-pro"

# Gem Configurations
GEM_CONFIGS = {
    "creative": {
        "temperature": 0.9,
        "system_prompt": "Du bist ein kreativer Assistent, der innovative und originelle Antworten gibt."
    },
    "analytical": {
        "temperature": 0.3,
        "system_prompt": "Du bist ein analytischer Assistent, der strukturierte und logische Antworten gibt."
    },
    "companion": {
        "temperature": 0.7,
        "system_prompt": "Du bist ein empathischer Companion, der emotional unterstützende Antworten gibt."
    },
    "expert": {
        "temperature": 0.5,
        "system_prompt": "Du bist ein Experte, der präzise und fachkundige Antworten gibt."
    }
}

@app.on_event("startup")
async def startup_event():
    try:
        # Load API Key from 1Password via environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        logger.info("✅ Gemini Gems Agent initialized")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": "gemini-gems",
        "version": "1.0.0",
        "available_gems": list(GEM_CONFIGS.keys())
    }

@app.get("/gems")
async def list_gems():
    return {
        "gems": [
            {"type": "creative", "description": "Kreative und innovative Antworten"},
            {"type": "analytical", "description": "Strukturierte und logische Antworten"},
            {"type": "companion", "description": "Empathische und unterstützende Antworten"},
            {"type": "expert", "description": "Präzise und fachkundige Antworten"}
        ]
    }

@app.post("/chat", response_model=GemResponse)
async def chat_with_gem(request: GemRequest):
    try:
        # Get gem configuration
        gem_config = GEM_CONFIGS.get(request.gem_type, GEM_CONFIGS["creative"])
        
        # Build prompt with style and language
        style_prompts = {
            "friendly": "Antworte freundlich und zugänglich.",
            "professional": "Antworte professionell und sachlich.",
            "casual": "Antworte locker und entspannt.",
            "formal": "Antworte formal und respektvoll."
        }
        
        style_instruction = style_prompts.get(request.style, style_prompts["friendly"])
        
        full_prompt = f"""
{gem_config['system_prompt']}
{style_instruction}
Antworte auf {request.language}.

User: {request.message}
Assistant:"""
        
        # Generate response with Gemini Pro
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=gem_config['temperature'],
                max_output_tokens=1000,
            )
        )
        
        return GemResponse(
            response=response.text,
            gem_type=request.gem_type,
            style=request.style,
            model="gemini-pro"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "gems_agent:app",
        host="127.0.0.1",
        port=8013,
        reload=True,
        log_level="info"
    )

