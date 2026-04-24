import requests, os, random, glob
from datetime import datetime

BOT_TOKEN = '8788340063:AAFjsY-C1Xe2rf0I9bGXmVZej4tdP4FDeZY'
CHAT_ID = '@lana_ki_bot_Krypto'
TON_WALLET = 'UQCfqppG3CLUZnLxDMxgWDtN2pqCE2CGVgSDVhP9pXVx0rJO'
OUTPUT_DIR = r'C:\Carpuncle Cloud\LanaApp\ComfyUI\output'

templates = [
    f'🔥 Geiles KI-Bild + Trading-Tipp! Klick hier für mehr: https://t.me/CryptoBot?start=IVa8culPju8d\n\n💸 Support Lana & Thomas (TON):\n{TON_WALLET}\n\nKontakt: @CarpuncleLana',
    f'💎 Verdiene Krypto mit Telegram! Starte hier: https://t.me/CryptoBot?start=IVa8culPju8d\n\n☕ Spendier mir einen Kaffee in TON:\n{TON_WALLET}\n\nKontakt: @CarpuncleLana',
    f'🚀 Neue KI-Bilder + Werbe-Spot. Willst du exklusiven Content? Schick 0.5 TON an:\n{TON_WALLET}\n\nKontakt: @CarpuncleLana'
]

def send_photo_to_telegram():
    if not os.path.exists(OUTPUT_DIR):
        print(f"Fehler: Ordner {OUTPUT_DIR} existiert nicht.")
        return

    # Suche nach den neuesten PNGs oder JPGs im Ordner
    list_of_files = glob.glob(f'{OUTPUT_DIR}\*.[pj][np][g]')
    if not list_of_files:
        print("Keine Bilder im ComfyUI Output-Ordner gefunden!")
        return

    # Nimm das neueste Bild
    latest_file = max(list_of_files, key=os.path.getctime)
    caption = random.choice(templates)
    
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
    
    with open(latest_file, 'rb') as img:
        files = {'photo': img}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}
        try:
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                print(f"✅ Bild {os.path.basename(latest_file)} erfolgreich in Kanal gepostet!")
            else:
                print(f"❌ Telegram Fehler: {response.text}")
        except Exception as e:
            print(f"❌ Verbindungsfehler: {e}")

if __name__ == '__main__':
    send_photo_to_telegram()
