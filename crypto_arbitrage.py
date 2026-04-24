import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

def check_arbitrage():
    # Binance API
    binance_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    # Coinbase API  
    coinbase_url = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
    
    try:
        binance_price = float(requests.get(binance_url).json()["price"])
        coinbase_data = requests.get(coinbase_url).json()
        coinbase_price = float(coinbase_data["data"]["rates"]["USD"])
        
        difference = abs(binance_price - coinbase_price)
        profit_percent = (difference / min(binance_price, coinbase_price)) * 100
        
        if profit_percent > 0.5:  # 0.5% Profit Schwelle
            print(f"🚨 ARBITRAGE CHANCE! Profit: {profit_percent:.2f}%")
            print(f"Binance: ${binance_price:.2f}")
            print(f"Coinbase: ${coinbase_price:.2f}")
            return True
        else:
            print(f"📊 Kein Arbitrage. Differenz: {profit_percent:.2f}%")
            return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    while True:
        check_arbitrage()
        time.sleep(30)  # Alle 30 Sekunden prüfen
