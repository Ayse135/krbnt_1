import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from core.banner_engine import BannerEngine

def test_uefa_render():
    engine = BannerEngine(
        "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat/1200x628_master.json",
        "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets"
    )
    
    # Test case 1: Long title that should wrap
    data_long = {
        "match_title": "SAMSUNSPOR ÇEYREK FİNAL YOLUNDA! BU AKŞAM DEV MAÇ VAR!",
        "day": "Perşembe",
        "hour": "20:30",
        "player_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_4.png",
        "player_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_2.png",
        "logo_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_1.png",
        "logo_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_2.png"
    }
    
    print("Rendering UEFA 1200x628 with long title...")
    path1 = engine.generate(data_long, size_key="1200x628", league="UEFA")
    print(f"Rendered to: {path1}")

    # Test case 2: Short title
    data_short = data_long.copy()
    data_short["match_title"] = "DEV MAÇ!"
    print("Rendering UEFA 1200x628 with short title...")
    path2 = engine.generate(data_short, size_key="1200x628", league="UEFA")
    print(f"Rendered to: {path2}")

if __name__ == "__main__":
    test_uefa_render()
