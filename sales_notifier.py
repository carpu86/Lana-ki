import requests
import json
from datetime import datetime
import time

# Ihr Telegram Bot Token (falls Sie einen haben)
TELEGRAM_BOT_TOKEN = "8788340063:AAFjsY-C1Xe2rf0I9bGXmVZej4tdP4FDeZY"
CHAT_ID = "IHR_CHAT_ID"  # Ihre Telegram Chat ID

def send_sale_notification(product, price):
    message = f"""
🎉 NEUER VERKAUF! 🎉

💰 Produkt: {product}
💵 Preis: €{price}
📅 Zeit: {datetime.now().strftime('%d.%m.%Y %H:%M')}

Gesamtumsatz heute: €{get_daily_revenue():.2f}
"""
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=data)
        print("✅ Verkaufs-Benachrichtigung gesendet!")
    except:
        print("📧 E-Mail Benachrichtigung würde hier gesendet...")

def get_daily_revenue():
    try:
        with open("daily_sales.json", "r") as f:
            sales = json.load(f)
        today = datetime.now().strftime('%Y-%m-%d')
        return sum([s["price"] for s in sales if s["date"] == today])
    except:
        return 0

def log_sale(product, price):
    sale = {
        "product": product,
        "price": float(price),
        "date": datetime.now().strftime('%Y-%m-%d'),
        "time": datetime.now().strftime('%H:%M:%S')
    }
    
    try:
        with open("daily_sales.json", "r") as f:
            sales = json.load(f)
    except:
        sales = []
    
    sales.append(sale)
    
    with open("daily_sales.json", "w") as f:
        json.dump(sales, f, indent=2)
    
    send_sale_notification(product, price)

if __name__ == "__main__":
    # Test-Verkäufe simulieren
    log_sale("AI Content Generator Pro", 19.99)
    log_sale("Crypto Trading Bot Elite", 97.00)
