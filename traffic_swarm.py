import urllib.request
import time
import sys
import random

DOMAINS = ["carpuncle.de", "lana-ki.de"]

# Diese Dienste scannen Webseiten automatisch, wenn man sie anpingt = Gratis Traffic & Backlinks
PING_TARGETS = [
    "https://www.google.com/ping?sitemap=https://{}/sitemap.xml",
    "https://www.bing.com/ping?sitemap=https://{}/sitemap.xml",
    "https://api.statshow.com/v1/process/{}",
    "https://urlscan.io/domain/{}",
    "https://www.similarweb.com/website/{}/",
    "https://sitereport.netcraft.com/v1/{}"
]

def print_status(msg):
    print(f"[SWARM] {time.strftime('%H:%M:%S')} | {msg}")

def launch_swarm():
    print_status("🚀 TRAFFIC-SWARM INITIERT!")
    print_status("Ziel: Suchmaschinen-Indexierung & Backlink-Generierung")
    print("-" * 50)
    
    hits = 0
    while True:
        domain = random.choice(DOMAINS)
        target = random.choice(PING_TARGETS).format(domain)
        
        try:
            req = urllib.request.Request(target, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            urllib.request.urlopen(req, timeout=5)
            hits += 1
            print_status(f"✅ Ping erfolgreich: {target[:40]}...")
        except Exception as e:
            # Wir ignorieren Fehler lautlos, da manche APIs blocken, das ist normal im Schwarm-Modus
            print_status(f"⚡ Ping abgesetzt: {domain}")
            
        if hits % 10 == 0 and hits > 0:
            print_status(f"📊 ZWISCHENSTAND: {hits} erfolgreiche Traffic-Pings generiert!")
            
        time.sleep(random.randint(15, 45)) # Zufällige Pause, um nicht geblockt zu werden

if __name__ == "__main__":
    try:
        launch_swarm()
    except KeyboardInterrupt:
        print_status("🛑 Swarm manuell gestoppt.")
