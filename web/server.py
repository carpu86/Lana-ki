import os, sqlite3, json, uuid, requests, datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
app = FastAPI()
DB_PATH = os.path.join(os.path.dirname(__file__), "lana_users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT, password TEXT, credits INTEGER, is_admin INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ownership (user_id TEXT, girl_id TEXT, has_media_access INTEGER, expiry_date DATETIME, PRIMARY KEY(user_id, girl_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS memory (user_id TEXT, girl_id TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS promo_codes (code TEXT PRIMARY KEY, girl_id TEXT, days INTEGER, used_count INTEGER DEFAULT 0)''')
    
    # Admin carpu anlegen (God Mode)
    c.execute("INSERT OR IGNORE INTO users VALUES ('000', 'carpu', 'Beatom#310886', 999999, 1)")
    # Promo Code Beispiel
    c.execute("INSERT OR IGNORE INTO promo_codes VALUES ('LANA2FREE', '001', 2, 0)")
    c.execute("INSERT OR IGNORE INTO promo_codes VALUES ('GIFT666', 'ALL', 7, 0)")
    
    conn.commit()
    conn.close()

init_db()
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

class ActionRequest(BaseModel):
    user_id: str
    girl_id: str
    action: str

@app.post("/api/check_access")
async def check_access(req: ActionRequest):
    if req.user_id == "000": return {"status": "granted", "message": "Willkommen, Commander."}
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT has_media_access, expiry_date FROM ownership WHERE user_id=? AND girl_id=?", (req.user_id, req.girl_id))
    access = c.fetchone()
    conn.close()

    if not access: return {"status": "locked", "message": "Zugriff verweigert."}
    
    # Check Expiry for Trials
    if access[1]:
        expiry = datetime.datetime.strptime(access[1], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() > expiry:
            return {"status": "locked", "message": "Testzeitraum abgelaufen."}

    return {"status": "granted"}

class PromoRequest(BaseModel):
    user_id: str
    code: str

@app.post("/api/redeem")
async def redeem(req: PromoRequest):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT girl_id, days FROM promo_codes WHERE code=?", (req.code,))
    promo = c.fetchone()
    
    if promo:
        gid, days = promo
        expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        # Wenn ALL, dann für alle 25 Girls? Hier beispielhaft für das eine Girl
        c.execute("INSERT OR REPLACE INTO ownership (user_id, girl_id, has_media_access, expiry_date) VALUES (?, ?, 0, ?)", 
                  (req.user_id, gid, expiry))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Code aktiviert! {days} Tage Zugriff freigeschaltet."}
    
    conn.close()
    return {"status": "error", "message": "Ungültiger Code."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
