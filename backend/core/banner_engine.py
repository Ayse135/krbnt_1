import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path

class BannerEngine:
    def __init__(self, master_prompt_path, assets_base_path, fonts_path=None):
        with open(master_prompt_path, "r", encoding="utf-8") as f:
            self.master = json.load(f)
        
        self.assets_path = Path(assets_base_path)
        # Yeni fontları tanımla (Monument Extended)
        ziraat_font_base = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat"
        self.fonts = {
            "ziraat_bold": os.path.join(ziraat_font_base, "MonumentExtended-Ultrabold.otf"),
            "ziraat_reg": os.path.join(ziraat_font_base, "MonumentExtended-Regular.otf"),
            "teko": "/Users/ayseguler/Library/Fonts/Teko[wght].ttf",
            "montserrat": "/Users/ayseguler/Library/Fonts/Montserrat[wght].ttf",
            "archivo": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ArchivoBlack-Regular.ttf"
        }
        self.default_bg = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_clean_1.png"

    def get_team_colors(self, team_name):
        """Takım renklerini döner (Primary, Secondary)"""
        colors = {
            "BEŞİKTAŞ": {"p": (0, 0, 0, 255), "s": (255, 255, 255, 255)},
            "GALATASARAY": {"p": (214, 0, 28, 255), "s": (252, 215, 0, 255)},
            "FENERBAHÇE": {"p": (0, 35, 71, 255), "s": (252, 215, 0, 255)},
            "TRABZONSPOR": {"p": (161, 30, 53, 255), "s": (0, 149, 218, 255)},
            "BAŞAKŞEHİR": {"p": (255, 102, 0, 255), "s": (0, 0, 128, 255)},
            "ANTALYASPOR": {"p": (255, 0, 0, 255), "s": (255, 255, 255, 255)},
            "RİZESPOR": {"p": (0, 107, 63, 255), "s": (255, 255, 255, 255)},
            "SAMSUNSPOR": {"p": (255, 0, 0, 255), "s": (255, 255, 255, 255)},
            "EYÜPSPOR": {"p": (128, 0, 128, 255), "s": (255, 255, 0, 255)}
        }
        return colors.get(team_name.upper(), {"p": (214, 0, 28, 255), "s": (255, 255, 255, 255)})

    def _colorize_image(self, image_rgba, color):
        """RGBA bir görüntüyü tinting (çarpma) yöntemiyle renklendirir, detayları korur"""
        if image_rgba.mode != "RGBA":
            image_rgba = image_rgba.convert("RGBA")
        r, g, b, a = image_rgba.split()
        cr, cg, cb = color[0]/255.0, color[1]/255.0, color[2]/255.0
        new_r = r.point(lambda i: int(i * cr))
        new_g = g.point(lambda i: int(i * cg))
        new_b = b.point(lambda i: int(i * cb))
        return Image.merge("RGBA", (new_r, new_g, new_b, a))

    def create_player_mask(self, size, radius=180):
        """Piller maskesi - Daha belirgin sol üst kavis (PSB spec)"""
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        w, h = size
        r = radius 
        draw.rectangle([0, r, w, h], fill=255)
        draw.rectangle([r, 0, w, r], fill=255)
        draw.pieslice([0, 0, 2*r, 2*r], 180, 270, fill=255)
        return mask

    def draw_text_with_spacing(self, draw, text, position, font, fill="white", spacing=0, target_width=None):
        """Metni belirli bir harf aralığı ile veya belirli bir genişliğe yayarak çizer"""
        x, y = position
        current_x = x
        
        if target_width:
            total_chars_width = sum(draw.textlength(c, font=font) for c in text)
            if len(text) > 1:
                spacing = (target_width - total_chars_width) / (len(text) - 1)
        
        for char in text:
            draw.text((current_x, y), char, font=font, fill=fill)
            current_x += draw.textlength(char, font=font) + spacing

    def generate_1200x628(self, data):
        width, height = self.master["size"]["width"], self.master["size"]["height"]
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        bg_custom = data.get("bg_photo_path")
        if bg_custom and os.path.exists(bg_custom):
            bg = Image.open(bg_custom).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
            canvas.paste(bg, (0, 0))
        else:
            bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_ultra_clean.png"
            if os.path.exists(bg_path):
                bg = Image.open(bg_path).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
                canvas.paste(bg, (0, 0))
            else:
                canvas.paste((214, 0, 28, 255), [0, 0, width, height])

        # Şablonları yükle (v2: Alpha kanalı korunmuş)
        template_dir = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates"
        glow_tpl = None
        outline_tpl = None
        if os.path.exists(os.path.join(template_dir, "backdrop_glow_v2.png")):
            glow_tpl = Image.open(os.path.join(template_dir, "backdrop_glow_v2.png")).convert("RGBA")
            outline_tpl = Image.open(os.path.join(template_dir, "backdrop_outline_v2.png")).convert("RGBA")

        for i in [1, 2]:
            v_player = self.master["variables"].get(f"player_{i}")
            p_img_path = data.get(f"player_{i}_path")
            
            if v_player:
                p_size = (v_player["width"], v_player["height"])
                p_pos = (v_player["left"], v_player["top"])
                team_name = data.get(f"team_{i}")
                t_colors = self.get_team_colors(team_name)
                
                # Arka Plan (Glow & Outline)
                if glow_tpl and outline_tpl:
                    b_size = (380, 480) 
                    glow = self._colorize_image(glow_tpl, t_colors["p"]).resize(b_size, Image.Resampling.LANCZOS)
                    outline = self._colorize_image(outline_tpl, t_colors["p"]).resize(b_size, Image.Resampling.LANCZOS)
                    
                    # Yerleşim: Oyuncunun (280x480) arkasında ortalanmış
                    # Glow ve Outline'ı biraz aşağı çekerek kafa taşma payı bırakıyoruz
                    b_pos = (p_pos[0] + (p_size[0] - b_size[0]) // 2, p_pos[1] + 60)
                    canvas.alpha_composite(glow, b_pos)
                    canvas.alpha_composite(outline, b_pos)

                # Oyuncu Maskeleme ve Pop-out (Kafa dışarıda)
                if p_img_path and os.path.exists(p_img_path):
                    p_img_source = Image.open(p_img_path).convert("RGBA")
                    pop_out = 70
                    p_full_size = (p_size[0], p_size[1] + pop_out)
                    p_img = ImageOps.fit(p_img_source, p_full_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                    
                    # Maske: Sadece alt kavisli kutuyu kes, üst (kafa) kısmını tam göster
                    p_mask = Image.new("L", p_full_size, 0)
                    inner_mask = self.create_player_mask(p_size, radius=130)
                    p_mask.paste(inner_mask, (0, pop_out))
                    
                    draw_m = ImageDraw.Draw(p_mask)
                    draw_m.rectangle([0, 0, p_full_size[0], pop_out], fill=255)
                    
                    p_final = Image.new("RGBA", p_full_size, (0,0,0,0))
                    p_final.paste(p_img, (0, 0), p_mask)
                    canvas.alpha_composite(p_final, (p_pos[0], p_pos[1] - pop_out))

        # Logo ve diğer öğeler
        for i in [1, 2]:
            v_logo = self.master["variables"].get(f"team_logo_{i}")
            l_img_path = data.get(f"logo_{i}_path")
            if v_logo and l_img_path and os.path.exists(l_img_path):
                l_img = Image.open(l_img_path).convert("RGBA").resize((v_logo["width"], v_logo["height"]))
                canvas.paste(l_img, (v_logo["left"], v_logo["top"]), l_img)

        for const in self.master["constants"]:
            name = const["name"].lower()
            if "nesine" in name and const["kind"] == "smartobject":
                n_path = self.assets_path / "branding" / "nesine_logo.png"
                if n_path.exists():
                    img = Image.open(n_path).convert("RGBA").resize((const["width"], const["height"]))
                    canvas.paste(img, (const["left"], const["top"]), img)
            elif "ziraat" in name and const["kind"] == "smartobject":
                z_path = self.assets_path / "branding" / "ziraat_logo.png"
                if z_path.exists():
                    img = Image.open(z_path).convert("RGBA").resize((const["width"], const["height"]))
                    canvas.paste(img, (const["left"], const["top"]), img)
            elif "hemen oyna" in name:
                ho_path = self.assets_path / "branding" / "hemen_oyna.png"
                if ho_path.exists():
                    img = Image.open(ho_path).convert("RGBA").resize((const["width"], const["height"]), Image.Resampling.LANCZOS)
                    canvas.paste(img, (const["left"], const["top"]), img)

        yellow_box_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/nesine_yellow_box.png"
        v_nesine_rect = next((c for c in self.master["constants"] if "rectangle 7" in c["name"].lower()), None)
        if v_nesine_rect and os.path.exists(yellow_box_path):
            y_box = Image.open(yellow_box_path).convert("RGBA").resize((v_nesine_rect["width"], v_nesine_rect["height"]), Image.Resampling.LANCZOS)
            canvas.paste(y_box, (v_nesine_rect["left"], v_nesine_rect["top"]), y_box)

        for i in [1, 2]:
            v_logo = self.master["variables"].get(f"team_logo_{i}")
            l_img_path = data.get(f"logo_{i}_path")
            if v_logo and l_img_path and os.path.exists(l_img_path):
                l_img = Image.open(l_img_path).convert("RGBA").resize((v_logo["width"], v_logo["height"]))
                canvas.paste(l_img, (v_logo["left"], v_logo["top"]), l_img)

        for const in self.master["constants"]:
            name = const["name"].lower()
            if "nesine" in name and const["kind"] == "smartobject":
                n_path = self.assets_path / "branding" / "nesine_logo.png"
                if n_path.exists():
                    img = Image.open(n_path).convert("RGBA").resize((const["width"], const["height"]))
                    canvas.paste(img, (const["left"], const["top"]), img)
            elif "ziraat" in name and const["kind"] == "smartobject":
                z_path = self.assets_path / "branding" / "ziraat_logo.png"
                if z_path.exists():
                    img = Image.open(z_path).convert("RGBA").resize((const["width"], const["height"]))
                    canvas.paste(img, (const["left"], const["top"]), img)
            elif "hemen oyna" in name:
                ho_path = self.assets_path / "branding" / "hemen_oyna.png"
                if ho_path.exists():
                    img = Image.open(ho_path).convert("RGBA").resize((const["width"], const["height"]), Image.Resampling.LANCZOS)
                    canvas.paste(img, (const["left"], const["top"]), img)

        draw = ImageDraw.Draw(canvas)
        # Fontlar (Monument Extended)
        font_teams = ImageFont.truetype(self.fonts["ziraat_bold"], 75)
        font_info = ImageFont.truetype(self.fonts["ziraat_reg"], 35)
        font_time = ImageFont.truetype(self.fonts["ziraat_reg"], 50)

        v_teams = self.master["variables"]["team_names_1"]
        target_team_w = 440 
        center_x = v_teams["left"] + v_teams["width"] // 2
        
        self.draw_text_with_spacing(draw, data['team_1'].upper(), (center_x - target_team_w//2, v_teams["top"] - 35), font_teams, fill="black", target_width=target_team_w)
        self.draw_text_with_spacing(draw, data['team_2'].upper(), (center_x - target_team_w//2, v_teams["top"] + 35), font_teams, fill="black", target_width=target_team_w)

        v_info = next(c for c in self.master["constants"] if "gün_saat" in c["name"].lower())
        target_info_w = 240
        info_center_x = v_info["left"] + v_info["width"] // 2
        
        self.draw_text_with_spacing(draw, data['hour'].upper(), (info_center_x - target_info_w//2, v_info["top"] - 15), font_time, fill="black", target_width=target_info_w)
        self.draw_text_with_spacing(draw, data['day'].upper(), (info_center_x - target_info_w//2, v_info["top"] + 25), font_info, fill="black", target_width=target_info_w)

        return canvas

    def generate_120x600(self, data):
        width, height = 120, 600
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_120x600_clean.png"
        if os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGBA")
            canvas.paste(bg, (0, 0))
        else:
            canvas.paste((214, 0, 28, 255), [0, 0, width, height])

        z_path = self.assets_path / "branding" / "ziraat_logo.png"
        if z_path.exists():
            img = Image.open(z_path).convert("RGBA").resize((41, 54))
            canvas.paste(img, (41, 28), img)

        p_y = 163
        for i in [1, 2]:
            p_img_path = data.get(f"player_{i}_path")
            p_x = 2 if i == 1 else 61
            p_size = (57, 77)
            side = "left" if i == 1 else "right"
            team_name = data.get(f"team_{i}")
            color = self.get_team_color(team_name)
            
            p_radius = 20
            p_outline = 3
            
            o_size = (p_size[0] + p_outline*2, p_size[1] + p_outline*2)
            o_mask = self.create_player_mask(o_size, radius=p_radius)
            o_img = Image.new("RGBA", o_size, color)
            canvas.paste(o_img, (p_x - p_outline, p_y - p_outline), o_mask)
            
            if p_img_path and os.path.exists(p_img_path):
                p_img_source = Image.open(p_img_path).convert("RGBA")
                p_img = ImageOps.fit(p_img_source, p_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                p_mask = self.create_player_mask(p_size, radius=p_radius)
                p_final = Image.new("RGBA", p_size, (0,0,0,0))
                p_final.paste(p_img, (0, 0), p_mask)
                canvas.paste(p_final, (p_x, p_y), p_final)

        l_y = 229
        for i in [1, 2]:
            l_path = data.get(f"logo_{i}_path")
            l_x = 13 if i == 1 else 69
            l_size = (36, 42) if i == 1 else (43, 43)
            if l_path and os.path.exists(l_path):
                l_img = Image.open(l_path).convert("RGBA").resize(l_size)
                canvas.paste(l_img, (l_x, l_y), l_img)

        draw = ImageDraw.Draw(canvas)
        font_teams = ImageFont.truetype(self.fonts["ziraat_bold"], 16)
        font_info = ImageFont.truetype(self.fonts["ziraat_reg"], 12)
        font_time = ImageFont.truetype(self.fonts["ziraat_reg"], 18)

        target_w = 110
        center_x = 60
        self.draw_text_with_spacing(draw, data['team_1'].upper(), (center_x - target_w//2, 309), font_teams, fill="black", target_width=target_w)
        self.draw_text_with_spacing(draw, data['team_2'].upper(), (center_x - target_w//2, 330), font_teams, fill="black", target_width=target_w)

        self.draw_text_with_spacing(draw, data['hour'].upper(), (center_x - target_w//2, 372), font_time, fill="black", target_width=target_w)
        self.draw_text_with_spacing(draw, data['day'].upper(), (center_x - target_w//2, 395), font_info, fill="black", target_width=target_w)

        ho_path = self.assets_path / "branding" / "hemen_oyna.png"
        if ho_path.exists():
            img = Image.open(ho_path).convert("RGBA").resize((83, 25))
            canvas.paste(img, (19, 460), img)

        yellow_box_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/nesine_yellow_box.png"
        if os.path.exists(yellow_box_path):
            y_box = Image.open(yellow_box_path).convert("RGBA").resize((133, 70), Image.Resampling.LANCZOS)
            canvas.paste(y_box, (-5, 542), y_box)

        n_path = self.assets_path / "branding" / "nesine_logo.png"
        if n_path.exists():
            img = Image.open(n_path).convert("RGBA").resize((78, 38), Image.Resampling.LANCZOS)
            canvas.paste(img, (22, 549), img)

        return canvas

    def generate_320x100(self, data):
        """3 sahneli 320x100 GIF banner üretir."""
        width, height = 320, 100
        bg_path = os.path.join(os.path.dirname(__file__), "..", "bg_320x100_clean.png")
        
        rgb_frames = []
        
        # --- SAHNE 1 ---
        from PIL import ImageEnhance
        base_bg = Image.open(bg_path).convert("RGBA")
        enhancer = ImageEnhance.Contrast(base_bg)
        frame1 = enhancer.enhance(1.1) 
        
        logo_path = os.path.join(os.path.dirname(__file__), "..", "ztk_yatay_logo.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            frame1.paste(logo, (85, 8), logo)
            
        bant_path = os.path.join(os.path.dirname(__file__), "..", "nesine_320x100_bant.png")
        if os.path.exists(bant_path):
            bant = Image.open(bant_path).convert("RGBA")
            frame1.paste(bant, (130, 68), bant)
        rgb_frames.append(frame1.convert("RGB"))
        
        # --- SAHNE 2 ---
        frame2 = Image.open(bg_path).convert("RGBA")
        p_size = (64, 87)
        p1_x, p1_y = 9, 3
        p2_x, p2_y = 243, 3
        
        for i in [1, 2]:
            px = p1_x if i == 1 else p2_x
            py = p1_y if i == 1 else p2_y
            side = "left" if i == 1 else "right"
            team_name = data.get(f"team_{i}")
            color = self.get_team_color(team_name)
            
            o_outline = 2
            o_size = (p_size[0] + o_outline*2, p_size[1] + o_outline*2)
            o_mask = self.create_player_mask(o_size, radius=15)
            o_img = Image.new("RGBA", o_size, color)
            frame2.paste(o_img, (px - o_outline, py - o_outline), o_mask)
            
            p_img_path = data.get(f"player_{i}_path")
            if p_img_path and os.path.exists(p_img_path):
                p_src = Image.open(p_img_path).convert("RGBA")
                p_img = ImageOps.fit(p_src, p_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                p_mask = self.create_player_mask(p_size, radius=15)
                p_final = Image.new("RGBA", p_size, (0,0,0,0))
                p_final.paste(p_img, (0, 0), p_mask)
                frame2.paste(p_final, (px, py), p_final)
 
        for i in [1, 2]:
            l_path = data.get(f"logo_{i}_path")
            lx = 68 if i == 1 else 200
            ly = 24
            l_size = (47, 59) if i == 1 else (56, 59)
            if l_path and os.path.exists(l_path):
                l_img = Image.open(l_path).convert("RGBA").resize(l_size, Image.Resampling.LANCZOS)
                frame2.paste(l_img, (lx, ly), l_img)
 
        ho_badge_path = os.path.join(os.path.dirname(__file__), "..", "hemen_oyna_320x100.png")
        if os.path.exists(ho_badge_path):
            ho_badge = Image.open(ho_badge_path).convert("RGBA")
            frame2.paste(ho_badge, (129, 43), ho_badge)
 
        if os.path.exists(bant_path):
            bant = Image.open(bant_path).convert("RGBA")
            frame2.paste(bant, (130, 68), bant)
        rgb_frames.append(frame2.convert("RGB"))
        
        # --- SAHNE 3 ---
        frame3 = Image.open(bg_path).convert("RGBA")
        draw3 = ImageDraw.Draw(frame3)
        
        try:
            ziraat_bold = self.fonts["ziraat_bold"]
            ziraat_reg = self.fonts["ziraat_reg"]
            font_main = ImageFont.truetype(ziraat_bold, 15)
            font_sub = ImageFont.truetype(ziraat_reg, 13)
            
            t1 = data.get('team_1', 'A').upper()
            t2 = data.get('team_2', 'B').upper()
            match_day = data.get('day', '...').upper()
            match_hour = data.get('hour', '...').upper()
            
            draw3.text((8, 26), t1, font=font_main, fill="black")
            draw3.text((8, 48), t2, font=font_main, fill="black")
            
            hour_box = draw3.textbbox((0, 0), match_hour, font=font_main)
            day_box = draw3.textbbox((0, 0), match_day, font=font_sub)
            
            draw3.text((312 - (hour_box[2]-hour_box[0]), 26), match_hour, font=font_main, fill="black")
            draw3.text((312 - (day_box[2]-day_box[0]), 48), match_day, font=font_sub, fill="black")
        except Exception:
            pass

        n_width, h_width = 60, 62
        gap = 10
        total_brand_w = n_width + gap + h_width
        start_x = (width - total_brand_w) // 2
        
        if os.path.exists(bant_path):
            bant = Image.open(bant_path).convert("RGBA")
            frame3.paste(bant, (start_x, 68), bant)
            
        if os.path.exists(ho_badge_path):
            ho_badge = Image.open(ho_badge_path).convert("RGBA")
            frame3.paste(ho_badge, (start_x + n_width + gap, 70), ho_badge)
            
        rgb_frames.append(frame3.convert("RGB"))
        
        # --- GIF SENTEZİ ---
        total_w = width * len(rgb_frames)
        combined = Image.new("RGB", (total_w, height))
        for i, frame in enumerate(rgb_frames):
            combined.paste(frame, (i * width, 0))
            
        global_palette_img = combined.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
        
        p_frames = []
        for img in rgb_frames:
            p_img = img.quantize(palette=global_palette_img, dither=Image.Dither.FLOYDSTEINBERG)
            p_frames.append(p_img)
            
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "output", "banner_320x100.gif")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        durations = [2000, 3500, 2500]
        
        p_frames[0].save(
            out_path, 
            save_all=True, 
            append_images=p_frames[1:], 
            duration=durations, 
            loop=0, 
            optimize=False, 
            disposal=2
        )
        
        return out_path

if __name__ == "__main__":
    # Test
    ENGINE = BannerEngine(
        "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat/1200x628_master.json",
        "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets"
    )
    test_data = {
        "team_1": "FENERBAHÇE",
        "team_2": "BEŞİKTAŞ",
        "day": "PAZAR",
        "hour": "21:00",
        "player_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_4.png",
        "player_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/players/player_2.png",
        "logo_1_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_1.png",
        "logo_2_path": "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/logos/logo_4.png"
    }
    result = ENGINE.generate_1200x628(test_data)
    result.save("/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/test_output_1200.png")
    print("Test üretimi tamamlandı: backend/test_output_1200.png")
