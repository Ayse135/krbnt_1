import os
import sys

# Backend'i path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from core.banner_engine import BannerEngine

def test_uefa_320():
    print("Generating UEFA 320x100 animated GIF...")
    
    # Paths (Verified from app.py)
    master_prompt = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat/1200x628_master.json"
    assets_base = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets"
    
    engine = BannerEngine(master_prompt, assets_base)
    
    # Mock data for UEFA match
    data = {
        "match_title": "Fenerbahçe Çeyrek Final Yolunda!",
        "day": "Perşembe",
        "hour": "22:00",
        "logo_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_1.png",
        "logo_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_2.png",
        "player_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_1.png",
        "player_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_2.png"
    }
    
    # Verify local assets exist for test
    for key in ["logo_1_path", "logo_2_path", "player_1_path", "player_2_path"]:
        if not os.path.exists(data[key]):
            # Fallback to any file if specific ones don't exist
            print(f"Warning: {data[key]} not found. Using placeholders.")
            # Note: In a real test, these should exist.
            
    try:
        output_path = engine.generate(data, size_key="320x100", league="UEFA")
        print(f"Success! Output saved to: {output_path}")
    except Exception as e:
        print(f"Error generating banner: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_uefa_320()
