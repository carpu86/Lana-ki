#!/usr/bin/env python3
# Microsoft Copilot Studio Agent für Lana-KI Platform

import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from msal import ConfidentialClientApplication
import uvicorn

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lana-KI Copilot Studio Agent", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class CopilotRequest(BaseModel):
    message: str
    conversation_id: str = None
    user_id: str = "default"

class CopilotResponse(BaseModel):
    response: str
    conversation_id: str
    agent: str = "copilot-studio"

# Global variables
msal_app = None
access_token = None

@app.on_event("startup")
async def startup_event():
    global msal_app
    try:
        # Initialize MSAL for Microsoft Graph/Copilot Studio
        tenant_id = os.getenv("AZURE_TENANT_ID")
        client_id = os.getenv("AZURE_CLIENT_ID") 
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        
        if not all([tenant_id, client_id, client_secret]):
            raise ValueError("Azure credentials not found")
        
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        msal_app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority
        )
        
        logger.info("✅ Copilot Studio Agent initialized")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

async def get_access_token():
    global access_token, msal_app
    try:
        # Get token for Microsoft Graph
        scopes = ["https://graph.microsoft.com/.default"]
        result = msal_app.acquire_token_for_client(scopes=scopes)
        
        if "access_token" in result:
            access_token = result["access_token"]
            return access_token
        else:
            raise Exception(f"Token acquisition failed: {result.get('error_description')}")
            
    except Exception as e:
        logger.error(f"Token error: {e}")
        raise

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": "copilot-studio",
        "version": "1.0.0",
        "msal_initialized": msal_app is not None
    }

@app.post("/chat", response_model=CopilotResponse)
async def chat_with_copilot(request: CopilotRequest):
    try:
        # Get access token
        token = await get_access_token()
        
        # TODO: Implement actual Copilot Studio API calls
        # For now, return a mock response
        mock_response = f"Copilot Studio Response zu: {request.message}"
        
        return CopilotResponse(
            response=mock_response,
            conversation_id=request.conversation_id or "new-conversation",
            agent="copilot-studio"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
async def list_conversations():
    try:
        # TODO: Implement conversation listing
        return {"conversations": [], "message": "Feature coming soon"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "copilot_agent:app",
        host="127.0.0.1",
        port=8012,
        reload=True,
        log_level="info"
    )

