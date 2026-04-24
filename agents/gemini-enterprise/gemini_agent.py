#!/usr/bin/env python3
# Gemini Enterprise Agent für Lana-KI Platform

import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from google.cloud import aiplatform
import uvicorn

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lana-KI Gemini Enterprise Agent", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str
    character_id: str = "default"
    temperature: float = 0.7
    max_tokens: int = 1000

class ChatResponse(BaseModel):
    response: str
    character_id: str
    model: str = "gemini-pro"

# Initialize Gemini
@app.on_event("startup")
async def startup_event():
    try:
        # Load API Key from 1Password via environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        
        # Initialize Vertex AI for Enterprise features
        project_id = os.getenv("GOOGLE_PROJECT_ID", "lana-ki-cloud-core")
        region = os.getenv("GOOGLE_REGION", "us-central1")
        
        aiplatform.init(project=project_id, location=region)
        
        logger.info("✅ Gemini Enterprise Agent initialized")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": "gemini-enterprise",
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_gemini(request: ChatRequest):
    try:
        # Character-specific prompts
        character_prompts = {
            "default": "Du bist Lana, eine freundliche KI-Assistentin.",
            "companion": "Du bist eine liebevolle KI-Companion, die emotional unterstützt.",
            "expert": "Du bist ein Experte in deinem Fachgebiet und gibst präzise Antworten."
        }
        
        system_prompt = character_prompts.get(request.character_id, character_prompts["default"])
        full_prompt = f"{system_prompt}\n\nUser: {request.message}\nAssistant:"
        
        # Generate response with Gemini Pro
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            )
        )
        
        return ChatResponse(
            response=response.text,
            character_id=request.character_id,
            model="gemini-pro"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-image")
async def generate_image(prompt: str):
    try:
        # Imagen integration für Enterprise
        # TODO: Implement Imagen API calls
        return {"message": "Image generation coming soon", "prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "gemini_agent:app",
        host="127.0.0.1",
        port=8011,
        reload=True,
        log_level="info"
    )

