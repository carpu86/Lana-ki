import requests
import time

# Ihre Verkaufs-Message
SALES_MESSAGE = """
🤖 REVOLUTIONÄRE KI-TOOLS VERFÜGBAR!

✅ AI Content Generator - Spart 20h/Woche
✅ Crypto Trading Bot - 15-25% monatliche Rendite  
✅ Komplett automatisiert - Keine Vorkenntnisse nötig

💰 Heute 50% Rabatt - Nur noch wenige Stunden!

🔗 Sofort kaufen: https://lana-ki-site.pages.dev/payment.html
💳 PayPal: https://paypal.me/Carpuncle86

⚡ Erste Kunden verdienen bereits €500+/Tag!
"""

# Deutsche Telegram Gruppen für Business/Krypto/KI
TARGET_GROUPS = [
    "@kryptotrading_de",
    "@business_deutschland", 
    "@geld_verdienen_online",
    "@affiliate_marketing_de",
    "@krypto_deutschland",
    "@online_business_de",
    "@passives_einkommen_de",
    "@trading_signals_de"
]

def send_to_groups():
    print("📱 SENDE MARKETING NACHRICHTEN...")
    for group in TARGET_GROUPS:
        print(f"📤 Sende an {group}")
        print(f"Message: {SALES_MESSAGE[:100]}...")
        print("✅ Gesendet! (Manuell in Telegram posten)")
        print("-" * 50)

if __name__ == "__main__":
    send_to_groups()
