from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3, os

app = FastAPI()
DB = os.environ.get('DB') or os.environ.get('OBEDIENCE_DB') or r'C:\\Carpuncle Cloud\\LanaApp\\data\\lana.db'

def init():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS memory (user TEXT, girl TEXT, role TEXT, content TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS subs (user TEXT, girl TEXT, media INTEGER)")
    conn.commit()
    conn.close()

init()

class Req(BaseModel):
    user_id: str
    girl_id: str
    message: str
    lehern_mode: bool = False

@app.post("/api/chat")
def chat(r: Req):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO memory VALUES (?,?,?,?)", (r.user_id, r.girl_id, "user", r.message))
    
    reply = f"*{r.girl_id}* Ich erinnere mich genau... " + ("Lass uns das gemeinsam verstehen." if r.lehern_mode else "Das hat mich tief berührt.")
    
    c.execute("INSERT INTO memory VALUES (?,?,?,?)", (r.user_id, r.girl_id, "assistant", reply))
    conn.commit()
    conn.close()
    return {"reply": reply, "memory_years": 10}

