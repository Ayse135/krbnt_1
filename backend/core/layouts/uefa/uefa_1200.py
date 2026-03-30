import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from ..base import BaseLayout

class UEFA1200(BaseLayout):
    def render(self, data):
        """Golden UEFA 1200x628 (Ported from 4da58c59 v22)."""
        width, height = 1200, 628
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(canvas)
        
        # 1. Config
        headless = not data.get("match_title")
        f_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_SemiExpanded-Bold.ttf"
        
        if headless:
            p_offset, title_y, day_y, hour_y = 240, 0, 90, 170
            logo_pos = [{"x": 145, "y": 120, "size": 180}, {"x": 1055, "y": 120, "size": 180}]
        else:
            p_offset, title_y, day_y, hour_y = 260, 40, 130, 220
            logo_pos = [{"x": 305, "y": 300, "size": 160}, {"x": 895, "y": 300, "size": 160}]

        # 2. Arka Plan (Shadow / Glow)
        anchors = [(width//2 - p_offset, 250), (width//2 + p_offset, 250)]
        for i in [1, 2]:
            p_path = data.get(f"player_{i}_path")
            if p_path and os.path.exists(p_path):
                # Ghost / Shadow
                ghost = Image.open(p_path).convert("RGBA")
                ghost = ImageOps.fit(ghost, (400, 600), Image.Resampling.LANCZOS)
                shadow = Image.new("RGBA", (400, 600), (0,0,0,0))
                shadow.paste((0, 191, 80, 120), [0, 0, 400, 600], ghost) # Neon Green Shadow
                shadow = shadow.filter(ImageFilter.GaussianBlur(15))
                canvas.alpha_composite(shadow, (anchors[i-1][0] - 200, anchors[i-1][1] - 300))

        # 3. Oyuncular (Pill Mask)
        for i in [1, 2]:
            p_path = data.get(f"player_{i}_path")
            if p_path and os.path.exists(p_path):
                p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), (340, 520), Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                p_mask = Image.new("L", (340, 520), 0)
                ImageDraw.Draw(p_mask).rounded_rectangle([0, 0, 340, 520], radius=40, fill=255)
                p_final = Image.new("RGBA", (340, 520), (0,0,0,0))
                p_final.paste(p_img, (0, 0), p_mask)
                canvas.alpha_composite(p_final, (anchors[i-1][0] - 170, anchors[i-1][1] - 260))

        # 4. Takım Logoları
        for i in [1, 2]:
            l_path = data.get(f"logo_{i}_path")
            if l_path and os.path.exists(l_path):
                l_img = Image.open(l_path).convert("RGBA")
                s = logo_pos[i-1]["size"]
                l_img.thumbnail((s, s), Image.Resampling.LANCZOS)
                canvas.alpha_composite(l_img, (logo_pos[i-1]["x"] - l_img.width//2, logo_pos[i-1]["y"] - l_img.height//2))

        # 5. Yazılar (Typography)
        try:
            font_title = ImageFont.truetype(f_path, 55)
            font_time = ImageFont.truetype(f_path, 70)
            
            if not headless:
                title = data.get('match_title', 'UEFA EUROPA LEAGUE').upper()
                tw = draw.textlength(title, font=font_title)
                draw.text(((width-tw)//2, title_y), title, font=font_title, fill="white")
            
            day_text = data.get('day', 'Perşembe').capitalize()
            hour_text = data.get('hour', '21:00')
            dw = draw.textlength(day_text, font=font_time)
            hw = draw.textlength(hour_text, font=font_time)
            draw.text(((width-dw)//2, day_y), day_text, font=font_time, fill="#06BF50") # Neon Green
            draw.text(((width-hw)//2, hour_y), hour_text, font=font_time, fill="white")
        except: pass

        # 6. Branding (UEFA Logo & Hemen Oyna)
        u_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/uefa_logo.png"
        if os.path.exists(u_path):
            u_img = Image.open(u_path).convert("RGBA")
            u_img.thumbnail((240, 110), Image.Resampling.LANCZOS)
            canvas.alpha_composite(u_img, ((width-u_img.width)//2, 330))

        # Save Output
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_uefa_1200.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        canvas.save(out_path)
        return out_path
