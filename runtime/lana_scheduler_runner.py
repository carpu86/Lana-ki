import time
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Carpuncle Cloud\LanaApp")
DB_FILE = ROOT / "data" / "lana.db"
LOG_FILE = ROOT / "logs" / "lana_scheduler.log"

def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def db():
    conn = sqlite3.connect(DB_FILE)
    return conn

def load_jobs():
    conn = db()
    rows = conn.execute("""
        SELECT id, name, cron, action, active
        FROM scheduler_jobs
        WHERE active = 1
        ORDER BY id ASC
    """).fetchall()
    conn.close()
    return rows

def run_action(job_id: int, name: str, action: str):
    log(f"RUN job_id={job_id} name={name} action={action}")

def main():
    log("Scheduler runner started")
    while True:
        try:
            jobs = load_jobs()
            for row in jobs:
                job_id, name, cron, action, active = row
                now = datetime.now()

                # Minimaler Start: einmal pro voller Minute bei cron='* * * * *'
                # oder nur Log für vorhandene Jobs
                if cron.strip() == "* * * * *" and now.second < 5:
                    run_action(job_id, name, action)
                elif cron.strip() == "0 9 * * *" and now.hour == 9 and now.minute == 0 and now.second < 5:
                    run_action(job_id, name, action)

            time.sleep(5)
        except Exception as e:
            log(f"ERROR {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    main()
