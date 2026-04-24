import os, uuid, chromadb, httpx
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Lana Memory Core")

DB_PATH = "/home/carpu/LanaApp/vector_memory"
os.makedirs(DB_PATH, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="lana_brain")

LOCAL_LLM_ENDPOINT = os.getenv("LOCAL_LLM_ENDPOINT", "http://100.110.207.22:1234/v1").rstrip("/")
EMBEDDING_URL = f"{LOCAL_LLM_ENDPOINT}/embeddings"

class MemoryData(BaseModel):
    user_text: str
    ai_text: str

class QueryData(BaseModel):
    text: str

async def get_embedding(text: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                EMBEDDING_URL,
                json={
                    "model": "text-embedding-nomic-embed-text-v1.5",
                    "input": text
                },
                timeout=10.0
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            print(f"Embedding Fehler: {e}")
            return None

@app.post("/memorize")
async def memorize(data: MemoryData):
    combined = f"User: {data.user_text}\nLana: {data.ai_text}"
    vector = await get_embedding(combined)
    if vector:
        collection.add(
            embeddings=[vector],
            documents=[combined],
            ids=[uuid.uuid4().hex]
        )
    return {"status": "memorized"}

@app.post("/recall")
async def recall(query: QueryData):
    vector = await get_embedding(query.text)
    if vector and collection.count() > 0:
        results = collection.query(query_embeddings=[vector], n_results=3)
        if results.get("documents") and results["documents"][0]:
            return {"context": " | ".join(results["documents"][0])}
    return {"context": ""}

if __name__ == "__main__":
    print("Lana Memory Core startet auf Port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
