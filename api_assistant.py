import webbrowser
import time

def open_api_sites():
    sites = {
        "Amazon Associates": "https://partnernet.amazon.de",
        "ClickBank": "https://accounts.clickbank.com/signup.htm",
        "PayPal Developer": "https://developer.paypal.com",
        "Stripe Dashboard": "https://dashboard.stripe.com/register",
        "CoinGecko API": "https://www.coingecko.com/en/api"
    }
    
    print("🚀 ÖFFNE ALLE API REGISTRIERUNGS-SEITEN...")
    
    for name, url in sites.items():
        print(f"📂 Öffne {name}...")
        webbrowser.open(url)
        time.sleep(2)  # 2 Sekunden warten zwischen Tabs
    
    print("\n✅ ALLE SEITEN GEÖFFNET!")
    print("📝 Registriere dich auf jeder Seite und kopiere die API Keys")

if __name__ == "__main__":
    open_api_sites()
