import time
import random

def generate_marketing_content():
    headlines = [
        "🚀 Verdienen Sie €500+ täglich mit KI!",
        "💰 Automatisches Einkommen durch AI-Tools!",
        "🎯 Von 0 auf €10.000/Monat in 30 Tagen!",
        "⚡ Revolutionäre KI-Tools jetzt verfügbar!",
        "🔥 Limitiertes Angebot: 50% Rabatt heute!"
    ]
    
    descriptions = [
        "Unsere KI-Tools haben bereits über 10.000 Menschen geholfen, ihr Einkommen zu verdoppeln!",
        "Vollautomatische Systeme, die 24/7 für Sie arbeiten - auch während Sie schlafen!",
        "Bewährte Strategien von Millionären, jetzt als KI-Tool verfügbar!",
        "Keine Vorkenntnisse nötig - alles wird automatisch für Sie erledigt!",
        "Starten Sie noch heute und sehen Sie erste Ergebnisse binnen 24 Stunden!"
    ]
    
    return {
        "headline": random.choice(headlines),
        "description": random.choice(descriptions),
        "cta": "Jetzt kaufen und sofort starten!"
    }

def create_social_media_posts():
    posts = []
    for i in range(5):
        content = generate_marketing_content()
        post = f"""
{content['headline']}

{content['description']}

🔗 Link: https://lana-ki-site.pages.dev/payment.html

#{i+1} #KI #Geld #Automation #Business
"""
        posts.append(post)
        print(f"📱 Social Media Post {i+1} erstellt!")
    
    with open("social_media_posts.txt", "w", encoding="utf-8") as f:
        f.write("\n" + "="*50 + "\n".join(posts))
    
    print("✅ 5 Marketing-Posts erstellt!")

if __name__ == "__main__":
    create_social_media_posts()
