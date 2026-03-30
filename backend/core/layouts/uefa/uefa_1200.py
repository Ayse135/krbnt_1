import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from ..base import BaseLayout

class UEFA1200(BaseLayout):
    def render(self, data):
        """PSD-Perfect UEFA 1200x628 Replication (Smaller Logos & Final Branding)."""
        width, height = 1200, 628
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(canvas)
        
        # 1. Config & Assets
        f_title = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat/MonumentExtended-Ultrabold.otf"
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_SemiExpanded-Bold.ttf"
        u_logo_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/uefa_logo.png"
        bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates/uefa_full_bg.png"

        # 2. Background
        if os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGBA")
            canvas.alpha_composite(bg, (0, 0))
        else:
            draw.rectangle([0, 0, width, height], fill=(0, 0, 0, 255))

        # 3. Takım Logoları (Küçültülmüş - Kullanıcı Talebi)
        # Orijinal Merkezler: Logo 1 [358, 229], Logo 2 [826, 228]
        # Yeni Boyutlar: ~20% Küçültme (yaklaşık 185x210)
        logos_data = [
            {"path": data.get("logo_1_path"), "center": (358, 229), "max_size": (185, 210)},
            {"path": data.get("logo_2_path"), "center": (826, 228), "max_size": (175, 210)}
        ]

        for l in logos_data:
            if l["path"] and os.path.exists(l["path"]):
                # Logo Glow (Hafif küçültülmüş yarıçap)
                self.draw_glow(canvas, l["center"], radius=140, color=(0, 191, 80, 60))
                
                l_img = Image.open(l["path"]).convert("RGBA")
                l_img.thumbnail(l["max_size"], Image.Resampling.LANCZOS)
                # Merkeze yerleştir
                canvas.alpha_composite(l_img, (l["center"][0] - l_img.width // 2, l["center"][1] - l_img.height // 2))

        # 4. Yazılar
        try:
            title = data.get('match_title', '').upper()
            if title:
                font_title = ImageFont.truetype(f_title, 55)
                tw = draw.textlength(title, font=font_title)
                draw.text(((width - tw) // 2, 30), title, font=font_title, fill="white")
            
            day_text = data.get('day', 'PAZARTESİ').upper()
            hour_text = data.get('hour', '20:30')
            font_info = ImageFont.truetype(f_saira, 60)
            
            dw = draw.textlength(day_text, font=font_info)
            draw.text(((width - dw) // 2, 160), day_text, font=font_info, fill="#06BF50")
            
            hw = draw.textlength(hour_text, font=font_info)
            draw.text(((width - hw) // 2, 222), hour_text, font=font_info, fill="white")
        except Exception as e:
            print(f"Typo Error: {e}")

        # 5. Branding (UEFA Logo & Hemen Oyna)
        if os.path.exists(u_logo_path):
            u_img = Image.open(u_logo_path).convert("RGBA")
            u_img = u_img.resize((81, 124), Image.Resampling.LANCZOS)
            canvas.alpha_composite(u_img, ((width - u_img.width) // 2, 323))

        ho_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/hemen_oyna.png"
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA")
            ho_img = ho_img.resize((190, 59), Image.Resampling.LANCZOS)
            canvas.alpha_composite(ho_img, (506, 465))

        draw.rectangle([492, 536, 492 + 217, 536 + 93], fill=(252, 215, 0))
        n_logo_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/nesine_logo.png"
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((180, 70), Image.Resampling.LANCZOS)
            canvas.alpha_composite(n_img, (492 + (217 - n_img.width) // 2, 536 + (93 - n_img.height) // 2))

        # 6. Save Output
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_uefa_1200.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        canvas.save(out_path)
        return out_path

    def draw_glow(self, canvas, pos, radius, color):
        """Standard UEFA radial glow."""
        x, y = pos
        glow = Image.new("RGBA", (radius*4, radius*4), (0,0,0,0))
        d = ImageDraw.Draw(glow)
        for r in range(radius, 0, -2):
            alpha = int(color[3] * (1 - r/radius))
            d.ellipse([2*radius-r, 2*radius-r, 2*radius+r, 2*radius+r], fill=(color[0], color[1], color[2], alpha))
        glow = glow.filter(ImageFilter.GaussianBlur(15))
        canvas.alpha_composite(glow, (x - 2*radius, y - 2*radius))
