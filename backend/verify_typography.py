from core.banner_engine import BannerEngine
import os

engine = BannerEngine(
    "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat/1200x628_master.json",
    "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets"
)

test_data = {
    "team_1": "ALANYASPOR",
    "team_2": "GALATASARAY",
    "day": "CUMA",
    "hour": "20:30",
    "player_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_4.png",
    "player_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_2.png",
    "logo_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_1.png",
    "logo_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_4.png"
}

print("Testing 1200x628...")
res_1200 = engine.generate_1200x628(test_data)
res_1200.save("/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/output/test_verify_1200.png")

print("Testing 120x600...")
res_120 = engine.generate_120x600(test_data)
res_120.save("/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/output/test_verify_120.png")

print("Testing 320x100 GIF...")
res_gif = engine.generate_320x100(test_data)
print(f"GIF saved to: {res_gif}")
