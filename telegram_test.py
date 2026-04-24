# TELEGRAM BOT TOKEN HIER EINFÜGEN:
# Beispiel: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_TOKEN = "HIER_DEIN_BOT_TOKEN"

# Test ob Bot funktioniert:
import requests
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
if response.status_code == 200:
    print("✅ Telegram Bot funktioniert!")
    print(f"Bot Name: {response.json()['result']['first_name']}")
else:
    print("❌ Bot Token ungültig")
