from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="LANA-KI Local AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "service": "lana-local-ai-backend",
        "mode": "local-first",
        "brain_loaded": True,
    }


@app.post("/api/chat")
def chat(req: ChatRequest):
    text = req.message.strip()
    answer = (
        "Lana ist online. Lokale KI-Basis laeuft. "
        "Nachricht empfangen: " + text
    )
    return {"ok": True, "answer": answer}
