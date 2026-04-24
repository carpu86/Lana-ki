import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_payment_request(chat_id, service, price):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice"
    
    payload = {
        "chat_id": chat_id,
        "title": f"🤖 {service}",
        "description": f"Premium {service} Service - Sofortige Lieferung!",
        "payload": f"{service}_{chat_id}",
        "provider_token": "DEIN_PAYMENT_PROVIDER_TOKEN",
        "currency": "EUR",
        "prices": [{"label": service, "amount": int(price * 100)}]
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Payment Request gesendet: €{price}")
            return True
        else:
            print(f"❌ Fehler: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def setup_money_bot():
    services = {
        "AI Content": 19.99,
        "Crypto Signals": 49.99,
        "Trading Bot": 97.00,
        "Premium Support": 29.99
    }
    
    print("💰 TELEGRAM GELD-BOT AKTIV!")
    print("Verfügbare Services:")
    for service, price in services.items():
        print(f"  💸 {service}: €{price}")
    
    return services

if __name__ == "__main__":
    setup_money_bot()
