import json
from datetime import datetime

def log_sale(product, price, payment_method):
    sale = {
        "timestamp": datetime.now().isoformat(),
        "product": product,
        "price": float(price),
        "payment_method": payment_method,
        "status": "completed"
    }
    
    try:
        with open("sales_log.json", "r") as f:
            sales = json.load(f)
    except:
        sales = []
    
    sales.append(sale)
    
    with open("sales_log.json", "w") as f:
        json.dump(sales, f, indent=2)
    
    total_revenue = sum([s["price"] for s in sales])
    print(f"💰 Neuer Verkauf: {product} - €{price}")
    print(f"🎯 Gesamt-Umsatz: €{total_revenue:.2f}")
    print(f"📊 Anzahl Verkäufe: {len(sales)}")

if __name__ == "__main__":
    # Test-Verkäufe loggen
    log_sale("AI Content Generator", 19.99, "PayPal")
    log_sale("Crypto Trading Bot", 97.00, "Stripe")
