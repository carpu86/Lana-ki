import requests
import time
import json
from datetime import datetime

class AutoTradingBot:
    def __init__(self):
        self.balance = 1000.0  # Start mit €1000 (Demo)
        self.positions = []
        self.profit = 0.0
        
    def get_crypto_price(self, symbol):
        """Hole aktuellen Krypto Preis"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=eur"
            response = requests.get(url)
            data = response.json()
            return data[symbol]['eur']
        except:
            return None
    
    def simple_strategy(self):
        """Einfache Buy Low, Sell High Strategie"""
        btc_price = self.get_crypto_price('bitcoin')
        eth_price = self.get_crypto_price('ethereum')
        
        if btc_price and eth_price:
            # Einfache Regel: Kaufe wenn Preis 2% gefallen ist
            # Verkaufe wenn Preis 3% gestiegen ist
            
            print(f"📊 BTC: €{btc_price:,.2f} | ETH: €{eth_price:,.2f}")
            print(f"💰 Balance: €{self.balance:.2f} | Profit: €{self.profit:.2f}")
            
            # Hier würde echte Trading Logik stehen
            # DEMO: Simuliere zufälligen kleinen Gewinn
            import random
            if random.random() > 0.6:  # 40% Chance auf Gewinn
                daily_profit = random.uniform(5, 25)
                self.profit += daily_profit
                self.balance += daily_profit
                print(f"✅ Gewinn: +€{daily_profit:.2f}")
            
            # Speichere Ergebnisse
            self.save_results()
    
    def save_results(self):
        """Speichere Trading Ergebnisse"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "balance": self.balance,
            "profit": self.profit
        }
        
        try:
            with open("trading_results.json", "r") as f:
                results = json.load(f)
        except:
            results = []
        
        results.append(result)
        
        with open("trading_results.json", "w") as f:
            json.dump(results, f, indent=2)
    
    def run_forever(self):
        """Laufe automatisch für immer"""
        print("🤖 AUTOMATISCHER TRADING BOT GESTARTET")
        print("=" * 50)
        
        while True:
            try:
                self.simple_strategy()
                print("⏰ Warte 1 Stunde bis zum nächsten Trade...")
                time.sleep(3600)  # 1 Stunde warten
            except KeyboardInterrupt:
                print("\n👋 Bot gestoppt!")
                break
            except Exception as e:
                print(f"❌ Fehler: {e}")
                time.sleep(300)  # 5 Minuten warten bei Fehler

if __name__ == "__main__":
    bot = AutoTradingBot()
    bot.run_forever()
