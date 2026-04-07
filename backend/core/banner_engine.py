import os
import json
from pathlib import Path

class BannerEngine:
    def __init__(self, master_prompt_path, assets_base_path, fonts_path=None):
        """Merkezi Asset ve Font yükleyici."""
        with open(master_prompt_path, "r", encoding="utf-8") as f:
            self.master = json.load(f)
        
        self.assets_path = Path(assets_base_path)
        ziraat_font_base = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat"
        self.fonts = {
            "ziraat_bold": os.path.join(ziraat_font_base, "MonumentExtended-Ultrabold.otf"),
            "ziraat_reg": os.path.join(ziraat_font_base, "MonumentExtended-Regular.otf"),
            "archivo": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ArchivoBlack-Regular.ttf"
        }

    def generate(self, data, size_key="1200x628", league="ZIRAAT", overrides=None):
        """Dispatcher: Lig ve Boyut hiyerarşisine göre uygun Layout'u çağırır."""
        league = league.upper()
        
        if league == "ZIRAAT":
            if size_key == "1200x628":
                from .layouts.ziraat.ziraat_1200 import Ziraat1200
                return Ziraat1200(self, overrides=overrides).render(data)
            elif size_key == "320x100":
                from .layouts.ziraat.ziraat_320 import Ziraat320
                return Ziraat320(self, overrides=overrides).render(data)
            elif size_key == "300x50":
                from .layouts.ziraat.ziraat_300 import Ziraat300
                return Ziraat300(self, overrides=overrides).render(data)
            elif size_key == "120x600":
                from .layouts.ziraat.ziraat_120 import Ziraat120
                return Ziraat120(self, overrides=overrides).render(data)
                
        elif league == "UEFA":
            if size_key == "1200x628":
                from .layouts.uefa.uefa_1200 import UEFA1200
                return UEFA1200(self, overrides=overrides).render(data)
            elif size_key == "120x600":
                from .layouts.uefa.uefa_120_600 import UEFA120_600
                return UEFA120_600(self, overrides=overrides).render(data)
            elif size_key == "320x100":
                from .layouts.uefa.uefa_320_100 import UEFA320_100
                return UEFA320_100(self, overrides=overrides).render(data)
            elif size_key == "300x50":
                from .layouts.uefa.uefa_300_50 import UEFA300_50
                return UEFA300_50(self, overrides=overrides).render(data)
            
        raise ValueError(f"Geçersiz hiyerarşi: {league} - {size_key}")
