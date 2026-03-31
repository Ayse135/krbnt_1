import os
import sys

# Backend'i path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from core.banner_engine import BannerEngine

def test_uefa_300_50():
    print("Generating UEFA 300x50 GIF (Step 1: BG Only)...")
    
    # Paths (Verified from app.py)
    master_prompt = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat/1200x628_master.json"
    assets_base = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets"
    
    engine = BannerEngine(master_prompt, assets_base)
    
    data = {
        "match_title": "Trabzonspor Manchester United",
        "day": "Perşembe",
        "hour": "22:00",
        "logo_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_1.png",
        "logo_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_2.png",
        "player_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_1.png",
        "player_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_2.png"
    }
    
    try:
        output_path = engine.generate(data, size_key="300x50", league="UEFA")
        print(f"Success! Output saved to: {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_uefa_300_50()
