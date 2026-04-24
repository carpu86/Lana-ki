#!/usr/bin/env python3
# Lana-KI Master Orchestrator

import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import uvicorn

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lana-KI Master Orchestrator", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent Configuration
AGENTS = {
    "gemini": {"url": "http://127.0.0.1:8011", "name": "Gemini Enterprise"},
    "copilot": {"url": "http://127.0.0.1:8012", "name": "Copilot Studio"},
    "gems": {"url": "http://127.0.0.1:8013", "name": "Gemini Gems"}
}

class UnifiedRequest(BaseModel):
    message: str
    agent: str = "auto"
    character_id: str = "default"
    temperature: float = 0.7

class UnifiedResponse(BaseModel):
    response: str
    agent_used: str
    status: str = "success"

@app.get("/health")
async def health_check():
    agent_status = {}
    
    async with httpx.AsyncClient() as client:
        for agent_id, config in AGENTS.items():
            try:
                response = await client.get(f"{config['url']}/health", timeout=5)
                agent_status[agent_id] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "name": config["name"]
                }
            except:
                agent_status[agent_id] = {
                    "status": "offline",
                    "name": config["name"]
                }
    
    return {
        "status": "healthy",
        "orchestrator": "lana-ki-master",
        "agents": agent_status
    }

@app.get("/agents")
async def list_agents():
    return {"agents": AGENTS}

def select_best_agent(message: str) -> str:
    """Intelligente Agent-Auswahl basierend auf der Nachricht"""
    message_lower = message.lower()
    
    # Keywords für verschiedene Agenten
    if any(word in message_lower for word in ["microsoft", "office", "excel", "word", "teams", "copilot"]):
        return "copilot"
    elif any(word in message_lower for word in ["kreativ", "creative", "story", "gedicht", "poem"]):
        return "gems"
    else:
        return "gemini"  # Default

@app.post("/chat", response_model=UnifiedResponse)
async def unified_chat(request: UnifiedRequest):
    try:
        # Agent-Auswahl
        if request.agent == "auto":
            selected_agent = select_best_agent(request.message)
        else:
            selected_agent = request.agent
        
        if selected_agent not in AGENTS:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {selected_agent}")
        
        agent_config = AGENTS[selected_agent]
        
        # Request an den gewählten Agenten
        async with httpx.AsyncClient() as client:
            # Payload je nach Agent anpassen
            if selected_agent == "gems":
                payload = {
                    "message": request.message,
                    "gem_type": "companion",
                    "style": "friendly"
                }
            elif selected_agent == "copilot":
                payload = {
                    "message": request.message,
                    "user_id": "orchestrator"
                }
            else:  # gemini
                payload = {
                    "message": request.message,
                    "character_id": request.character_id,
                    "temperature": request.temperature
                }
            
            response = await client.post(
                f"{agent_config['url']}/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return UnifiedResponse(
                    response=result.get("response", "Keine Antwort erhalten"),
                    agent_used=f"{selected_agent} ({agent_config['name']})"
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Agent {selected_agent} error: {response.text}"
                )
    
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "orchestrator:app",
        host="127.0.0.1",
        port=8010,
        reload=True,
        log_level="info"
    )

