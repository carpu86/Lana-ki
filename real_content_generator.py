import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

class AIContentGenerator:
    def __init__(self):
        self.api_key = GEMINI_KEY
        
    def generate_blog_post(self, topic, word_count=500):
        prompt = f"""
        Schreibe einen professionellen Blog-Artikel über "{topic}".
        
        Anforderungen:
        - {word_count} Wörter
        - SEO-optimiert
        - Mit Überschriften (H2, H3)
        - Einleitung, Hauptteil, Fazit
        - Call-to-Action am Ende
        
        Stil: Professionell, informativ, engaging
        """
        return self._call_gemini(prompt)
    
    def generate_social_media_posts(self, topic, platform="Instagram"):
        prompt = f"""
        Erstelle 5 {platform} Posts über "{topic}".
        
        Für jeden Post:
        - Catchy Headline
        - Engaging Text (max 150 Wörter)
        - 5-10 relevante Hashtags
        - Call-to-Action
        
        Stil: Modern, ansprechend, viral-tauglich
        """
        return self._call_gemini(prompt)
    
    def generate_email_sequence(self, product, audience):
        prompt = f"""
        Erstelle eine 5-teilige E-Mail Sequenz für "{product}".
        Zielgruppe: {audience}
        
        E-Mail 1: Willkommen + Problem aufzeigen
        E-Mail 2: Lösung präsentieren  
        E-Mail 3: Social Proof + Testimonials
        E-Mail 4: Urgency + limitiertes Angebot
        E-Mail 5: Letzter Aufruf + Bonus
        
        Jede E-Mail: Betreff + Volltext + Call-to-Action
        """
        return self._call_gemini(prompt)
    
    def _call_gemini(self, prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"Fehler: {response.status_code}"
        except Exception as e:
            return f"Fehler: {e}"

# Einfache Benutzeroberfläche
if __name__ == "__main__":
    generator = AIContentGenerator()
    
    print("🤖 AI CONTENT GENERATOR PRO")
    print("=" * 40)
    
    while True:
        print("\nWas möchten Sie erstellen?")
        print("1. Blog-Artikel")
        print("2. Social Media Posts") 
        print("3. E-Mail Sequenz")
        print("4. Beenden")
        
        choice = input("\nIhre Wahl (1-4): ")
        
        if choice == "1":
            topic = input("Thema des Blog-Artikels: ")
            words = input("Anzahl Wörter (Standard: 500): ") or "500"
            print("\n🔄 Generiere Blog-Artikel...")
            result = generator.generate_blog_post(topic, int(words))
            
            filename = f"blog_{topic.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ Blog-Artikel gespeichert: {filename}")
            
        elif choice == "2":
            topic = input("Thema für Social Media: ")
            platform = input("Plattform (Instagram/Facebook/LinkedIn): ") or "Instagram"
            print("\n🔄 Generiere Social Media Posts...")
            result = generator.generate_social_media_posts(topic, platform)
            
            filename = f"social_{platform}_{topic.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ Social Media Posts gespeichert: {filename}")
            
        elif choice == "3":
            product = input("Produkt/Service: ")
            audience = input("Zielgruppe: ")
            print("\n🔄 Generiere E-Mail Sequenz...")
            result = generator.generate_email_sequence(product, audience)
            
            filename = f"email_sequence_{product.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ E-Mail Sequenz gespeichert: {filename}")
            
        elif choice == "4":
            print("👋 Auf Wiedersehen!")
            break
        else:
            print("❌ Ungültige Eingabe!")
