import sys
import os
from dotenv import load_dotenv, set_key

ENV_FILE = "C:\\Carpuncle Cloud\\LanaApp\\.env"

def update_tunnel(url):
    # Speichert die Colab URL sicher in der .env Datei
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'w') as f:
            f.write("")
    
    set_key(ENV_FILE, "COLAB_TUNNEL_URL", url)
    print(f"✅ Colab Pro Tunnel-URL wurde im System registriert!")
    print(f"🔗 Aktive GPU-Brücke: {url}")
    print("Lana wird ab sofort diese URL für schwere Berechnungen nutzen.")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "connect":
        tunnel_url = sys.argv[2]
        update_tunnel(tunnel_url)
    else:
        print("Verwendung: python colab_pro.py connect <deine-trycloudflare-url>")
