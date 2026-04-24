import requests
import json
from datetime import datetime

# DEINE ECHTE TON WALLET ADRESSE
TON_WALLET = "UQCfqppG3CLUZnLxDMxgWDtN2pqCE2CGVgSDVhP9pXVx0rJO"

# Telegram Bot für Notifications
TELEGRAM_BOT_TOKEN = "8788340063:AAFjsY-C1Xe2rf0I9bGXmVZej4tdP4FDeZY"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # Deine Chat ID

def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
    except:
        pass

def check_ton_balance():
    try:
        # TON API Abfrage
        response = requests.get(f"https://toncenter.com/api/v2/getAddressInformation?address={TON_WALLET}")
        data = response.json()
        
        if data.get("ok"):
            balance = int(data["result"]["balance"]) / 1000000000  # Convert from nanotons
            
            send_telegram_notification(f"""
💎 <b>TON WALLET UPDATE</b>
💰 Balance: {balance:.6f} TON
📍 Wallet: {TON_WALLET[:10]}...
⏰ Zeit: {datetime.now().strftime('%H:%M:%S')}
            """)
            
            return balance
        return 0
    except:
        return 0

if __name__ == "__main__":
    balance = check_ton_balance()
    print(f"Current TON Balance: {balance:.6f} TON")
