import sqlite3, os
db = r"C:\Carpuncle Cloud\LanaApp\data\lana.db"
print("exists:", os.path.exists(db))
try:
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS __sanitytest(id INTEGER PRIMARY KEY, created_at TEXT)")
    conn.commit()
    conn.close()
    print("sqlite OPEN & sanity test OK")
except Exception as e:
    print("ERROR:", e)
