from typing import Optional
from fastapi import FastAPI, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import uvicorn
from dotenv import load_dotenv
import os

from core.banner_engine import BannerEngine
import base64
from io import BytesIO

load_dotenv()

app = FastAPI(title="KRBNT Banner Motoru - Hibrit PSD + AI")

# Engine'i başlat
ENGINE = BannerEngine(
    "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat/1200x628_master.json",
    "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Output klasörünü oluştur
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

@app.post("/generate-banner")
async def generate_banner(
    league: str = Form(...),
    size: str = Form(...),
    team_1: str = Form(...),
    team_2: str = Form(...),
    day: str = Form(...),
    hour: str = Form(...),
    match_title: str = Form(default="SAMSUNSPOR ÇEYREK FİNAL YOLUNDA!"),
    player_1_id: str = Form(default="1"),
    player_2_id: str = Form(default="2")
):
    try:
        # Logo haritalama (Basit versiyon)
        logo_map = {
            "BEŞİKTAŞ": "1",
            "GALATASARAY": "2",
            "FENERBAHÇE": "3",
            "TRABZONSPOR": "4",
            "BAŞAKŞEHİR": "5",
            "SAMSUNSPOR": "6",
            "GAZİANTEP FK": "1",
            "RİZESPOR": "4"
        }
        
        l1_id = logo_map.get(team_1.upper(), "1")
        l2_id = logo_map.get(team_2.upper(), "2")

        data = {
            "team_1": team_1,
            "team_2": team_2,
            "day": day,
            "hour": hour,
            "match_title": match_title,
            "player_1_path": f"/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_{player_1_id}.png",
            "player_2_path": f"/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_{player_2_id}.png",
            "logo_1_path": f"/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_{l1_id}.png",
            "logo_2_path": f"/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_{l2_id}.png"
        }
        
        # Dispatch to the modular engine
        generated_path = ENGINE.generate(data, size_key=size, league=league)
        filename = os.path.basename(generated_path)
        
        # Static URL döndür
        return {
            "status": "success",
            "imageUrl": f"http://127.0.0.1:8000/output/{filename}?v={os.urandom(4).hex()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Static dosyaları aç (Router en sonda olmalı yoksa POST'ları keser)
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
