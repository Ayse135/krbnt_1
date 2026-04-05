from typing import Optional
from fastapi import FastAPI, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
    expose_headers=["Content-Disposition"],
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
    player_2_id: str = Form(default="2"),
    overrides: Optional[str] = Form(None)
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
        
        # overrides string'ini dict'e çevir
        import json
        overrides_dict = None
        if overrides:
            try:
                overrides_dict = json.loads(overrides)
            except Exception as e:
                print(f"Overrides Parse Error: {e}")

        # Dispatch to the modular engine with overrides
        generated_path = ENGINE.generate(data, size_key=size, league=league, overrides=overrides_dict)
        filename = os.path.basename(generated_path)
        
        # Relative URL döndür (Host bağımsızlığı için)
        return {
            "status": "success",
            "imageUrl": f"/output/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ⚠️ ÖNEMLI SIRALAMA:
# app.mount() sonrasında eklenen route'lar mount tarafından gölgelenir ve çalışmaz!
# Bu yüzden tüm route'lar mount'lardan ÖNCE tanımlanmalıdır.

# İndirme Butonu için Zorunlu İndirme Rotası (mount'lardan ÖNCE olmalı!)
@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    content_type = "image/png"
    if filename.endswith(".gif"):
        content_type = "image/gif"
        
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=content_type,
        headers={"Access-Control-Expose-Headers": "Content-Disposition"}
    )

# Görüntüleme için Standart Statik Dosya Hizmeti (route'lardan SONRA olmalı)
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

# Frontend mount (Her zaman en sonda olmalı yoksa diğer rotaları ezer!)
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
