import os
import json
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from pathlib import Path

class BannerEngine:
    def __init__(self, master_prompt_path, assets_base_path, fonts_path=None):
        with open(master_prompt_path, "r", encoding="utf-8") as f:
            self.master = json.load(f)
        
        self.assets_path = Path(assets_base_path)
        # Yeni fontları tanımla (Monument Extended + UEFA Saira)
        ziraat_font_base = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat"
        uefa_font_base = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa"
        self.fonts = {
            "ziraat_bold": os.path.join(ziraat_font_base, "MonumentExtended-Ultrabold.otf"),
            "ziraat_reg": os.path.join(ziraat_font_base, "MonumentExtended-Regular.otf"),
            "uefa_bold": os.path.join(uefa_font_base, "Saira_Expanded-Bold.ttf"),
            "uefa_reg": os.path.join(uefa_font_base, "Saira_Expanded-Regular.ttf"),
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

    def apply_glow(self, img, color=(6, 191, 80), radius=55, opacity=220):
        """Creates a high-power 'High-Voltage' Aura with dual-core density (v22)."""
        padding = radius * 3
        padded_size = (img.width + padding * 2, img.height + padding * 2)
        
        expanded_img = Image.new("RGBA", padded_size, (0, 0, 0, 0))
        expanded_img.paste(img, (padding, padding))
        mask = expanded_img.split()[-1]
        
        # 1. Dilation for the Gap
        dilated_mask = mask.filter(ImageFilter.MaxFilter(size=9))
        
        # 2. Dual-Core Generation
        glow_color_img = Image.new("RGBA", padded_size, color + (opacity,))
        
        # PASS A: Broad Aura (Environmental Reach)
        aura_glow = Image.new("RGBA", padded_size, (0,0,0,0))
        aura_glow.paste(glow_color_img, (0,0), dilated_mask)
        aura_glow = aura_glow.filter(ImageFilter.GaussianBlur(radius))
        
        # PASS B: Inner Core (Brilliancy/Punch)
        core_radius = max(10, radius // 3)
        core_glow = Image.new("RGBA", padded_size, (0,0,0,0))
        core_glow.paste(glow_color_img, (0,0), dilated_mask)
        core_glow = core_glow.filter(ImageFilter.GaussianBlur(core_radius))
        
        # 3. Mixing and High-Voltage Saturation (Quadruple-Pass)
        power_composite = Image.new("RGBA", padded_size, (0,0,0,0))
        power_composite.alpha_composite(aura_glow)
        power_composite.alpha_composite(core_glow)
        power_composite.alpha_composite(core_glow) # Double Core for "Burn"
        power_composite.alpha_composite(aura_glow) # Double Aura for environmental fill
        
        # 4. Final Assembly
        final = Image.new("RGBA", padded_size, (0,0,0,0))
        final.alpha_composite(power_composite)
        final.alpha_composite(expanded_img)
        return final

    def draw_nesine_uefa_box(self, canvas, pos, width=217, height=93):
        """Draws the special UEFA Nesine branding box matching PSD exactly."""
        draw = ImageDraw.Draw(canvas)
        # Yellow Rectangle
        draw.rectangle([pos[0], pos[1], pos[0] + width, pos[1] + height], fill="#FFCC00")
        
        # Nesine Logo (Already contains 'BAŞKA BİR SEVİYE')
        n_path = self.assets_path / "branding" / "nesine_logo.png"
        if n_path.exists():
            n_img = Image.open(n_path).convert("RGBA")
            # PSD Scale: 141x68
            n_w, n_h = 141, 68
            n_img = ImageOps.fit(n_img, (n_w, n_h), method=Image.Resampling.LANCZOS)
            # PSD Positioning: 12px padding from top (PSD y=548, box y=536)
            canvas.paste(n_img, (pos[0] + (width - n_w) // 2, pos[1] + 12), n_img)

    def create_player_mask(self, size, radius=130, asymmetric=True):
        """Piller maskesi - Asimetrik (Sol üst kavisli) veya Tam Pill desteği"""
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        w, h = size
        # Güvenlik kontrolü: Radius boyutları aşmamalı
        r = min(radius, w // 2, h // 2) 
        
        if asymmetric:
            draw.rectangle([0, r, w, h], fill=255)
            draw.rectangle([r, 0, w, r], fill=255)
            draw.pieslice([0, 0, 2*r, 2*r], 180, 270, fill=255)
        else:
            # Tam Pill (Üst ve alt kavisli)
            draw.rectangle([0, r, w, h-r], fill=255)
            draw.pieslice([0, 0, 2*r, 2*r], 180, 270, fill=255)
            draw.pieslice([w-2*r, 0, w, 2*r], 270, 0, fill=255)
            draw.pieslice([w-2*r, h-2*r, w, h], 0, 90, fill=255)
            draw.pieslice([0, h-2*r, 2*r, h], 90, 180, fill=255)
            draw.rectangle([r, 0, w-r, h], fill=255)
        return mask

    def draw_radial_glow(self, size, color):
        """Merkezden dışa doğru radyal bir ışıma oluşturur"""
        glow = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)
        w, h = size
        cx, cy = w // 2, h // 2
        max_dim = max(w, h)
        
        for r in range(max_dim, 0, -5):
            alpha = int(200 * (1 - r/max_dim))
            if alpha <= 0: continue
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(color[0], color[1], color[2], alpha))
        return glow

    def draw_procedural_backdrop(self, t_colors, size):
        """PSD Fidelity: Base + Glow + Waves + Outline katmanlarını birleştirir"""
        b_canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        
        # 1. Maske (Asimetrik)
        mask = self.create_player_mask(size, radius=180)
        
        # 2. Taban (Primary Color)
        base = Image.new("RGBA", size, t_colors["p"])
        
        # 3. Radial Glow (Işıma)
        glow = self.draw_radial_glow(size, (255, 255, 255))
        base.alpha_composite(glow)
        
        # 4. Wave Texture (Dalgalı Doku - Şablondan)
        wave_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates/backdrop_waves_v3.png"
        if os.path.exists(wave_path):
            waves = Image.open(wave_path).convert("L").resize(size, Image.Resampling.LANCZOS)
            wave_overlay = Image.new("RGBA", size, (255, 255, 255, 40)) # Hafif beyaz dalgalar
            base.paste(wave_overlay, (0, 0), waves)
            
        b_canvas.paste(base, (0, 0), mask)
        
        # 5. Outline (Secondary Color - 10px Stroke)
        outline_mask = self.create_player_mask((size[0]+20, size[1]+20), radius=190)
        outline_img = Image.new("RGBA", (size[0]+20, size[1]+20), t_colors["s"])
        
        final_b = Image.new("RGBA", (size[0]+20, size[1]+20), (0, 0, 0, 0))
        final_b.paste(outline_img, (0, 0), outline_mask)
        final_b.alpha_composite(b_canvas, (10, 10))
        
        return final_b


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

    def generate_1200x628(self, data, league="ZIRAAT"):
        width, height = self.master["size"]["width"], self.master["size"]["height"]
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        template_dir = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates"

        # Lig bazlı Arka Plan
        if league.upper() == "UEFA":
            canvas.paste((0, 0, 0, 255), [0, 0, width, height]) # Solid Black
            tex_path = os.path.join(template_dir, "uefa_bg_textures.png")
            if os.path.exists(tex_path):
                tex = Image.open(tex_path).convert("RGBA")
                # PSD Coordinate: Left -933, Top -906 (Original was 2849x2255)
                canvas.alpha_composite(tex, (-933, -906))
            
            f_bold = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_SemiExpanded-Bold.ttf"
            f_reg = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_SemiExpanded-Regular.ttf"
        else:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "ztk_yatay_logo.png")
            f_bold = self.fonts["ziraat_bold"]
            f_reg = self.fonts["ziraat_reg"]
            
            # Ziraat Background
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

        # Player Rendering (Conditional Bypass for UEFA v16)
        if league.upper() != "UEFA":
            for i in [1, 2]:
                v_player = self.master["variables"].get(f"player_{i}")
                p_img_path = data.get(f"player_{i}_path")
                
                if v_player:
                    p_size = (v_player["width"], v_player["height"])
                    p_pos = (v_player["left"], v_player["top"])
                    
                    team_name = data.get(f"team_{i}")
                    t_colors = self.get_team_colors(team_name)
                    
                    # Ziraat Backdrop
                    b_size = (380, 480)
                    b_final = self.draw_procedural_backdrop(t_colors, b_size)
                    b_pos = (p_pos[0] + (p_size[0] - b_size[0]) // 2 - 10, p_pos[1] + 60 - 10)
                    canvas.alpha_composite(b_final, b_pos)

                    # Oyuncu Maskeleme (Ziraat)
                    if p_img_path and os.path.exists(p_img_path):
                        p_img_source = Image.open(p_img_path).convert("RGBA")
                        pop_out = 140
                        p_full_size = (p_size[0], p_size[1] + pop_out)
                        p_img = ImageOps.fit(p_img_source, p_full_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                        
                        p_mask = Image.new("L", p_full_size, 0)
                        inner_shape_mask = self.create_player_mask(p_size, radius=130)
                        p_mask.paste(inner_shape_mask, (0, pop_out))
                        p_mask.paste(255, [0, 0, p_size[0], pop_out]) 
                        
                        p_final = Image.new("RGBA", p_full_size, (0,0,0,0))
                        p_final.paste(p_img, (0, 0), p_mask)
                        canvas.alpha_composite(p_final, (p_pos[0], p_pos[1] - pop_out))

        # Logos (Moved after players for consistency)
        if league.upper() == "UEFA":
            # UEFA Logo Compositional Alignment (v10)
            # Smaller scale (150x150) centered on PSD's logo mid-points
            uefa_logo_positions = [
                {"top": 140, "left": 272, "width": 150, "height": 150},
                {"top": 140, "left": 775, "width": 150, "height": 150}
            ]
            for i in [1, 2]:
                l_img_path = data.get(f"logo_{i}_path")
                if l_img_path and os.path.exists(l_img_path):
                    v_logo = uefa_logo_positions[i - 1]
                    l_img = Image.open(l_img_path).convert("RGBA").resize((v_logo["width"], v_logo["height"]), Image.Resampling.LANCZOS)
                    # Apply Floating Diffused Aura (v20 Calibrated - #06BF50)
                    glow_color = (6, 191, 80) 
                    radius = 55
                    l_glow = self.apply_glow(l_img, color=glow_color, radius=radius, opacity=220)
                    
                    # Padding in v20 is radius * 3 (165px)
                    canvas.alpha_composite(l_glow, (v_logo["left"] - radius*3, v_logo["top"] - radius*3))
        else:
            # Ziraat Logo Positions (from Master JSON)
            for i in [1, 2]:
                v_logo = self.master["variables"].get(f"team_logo_{i}")
                l_img_path = data.get(f"logo_{i}_path")
                if v_logo and l_img_path and os.path.exists(l_img_path):
                    l_img = Image.open(l_img_path).convert("RGBA").resize((v_logo["width"], v_logo["height"]))
                    canvas.paste(l_img, (v_logo["left"], v_logo["top"]), l_img)

        # Static Branding Constants
        if league.upper() != "UEFA":
            for const in self.master["constants"]:
                name = const["name"].lower()
                if "nesine" in name and const["kind"] == "smartobject":
                    n_path = self.assets_path / "branding" / "nesine_logo.png"
                    if n_path.exists():
                        img = Image.open(n_path).convert("RGBA").resize((const["width"], const["height"]))
                        canvas.paste(img, (const["left"], const["top"]), img)
                elif "ziraat" in name and const["kind"] == "smartobject":
                    z_path = os.path.join(os.path.dirname(__file__), "..", "ztk_yatay_logo.png")
                    if os.path.exists(z_path):
                        img = Image.open(z_path).convert("RGBA").resize((const["width"], const["height"]), Image.Resampling.LANCZOS)
                        canvas.paste(img, (const["left"], const["top"]), img)
                elif "hemen oyna" in name:
                    ho_path = self.assets_path / "branding" / "hemen_oyna.png"
                    if ho_path.exists():
                        img = Image.open(ho_path).convert("RGBA").resize((const["width"], const["height"]), Image.Resampling.LANCZOS)
                        canvas.paste(img, (const["left"], const["top"]), img)

            # Yellow Box
            yellow_box_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/nesine_yellow_box.png"
            v_nesine_rect = next((c for c in self.master["constants"] if "rectangle 7" in c["name"].lower()), None)
            if v_nesine_rect and os.path.exists(yellow_box_path):
                y_box = Image.open(yellow_box_path).convert("RGBA").resize((v_nesine_rect["width"], v_nesine_rect["height"]), Image.Resampling.LANCZOS)
                canvas.paste(y_box, (v_nesine_rect["left"], v_nesine_rect["top"]), y_box)

        draw = ImageDraw.Draw(canvas)
        
        if league.upper() == "UEFA":
            # --- UEFA Layout: Title Top, Time Center ---
            
            # Draw Main Title
            font_title = ImageFont.truetype(f_bold, 55)
            title_text = data.get('match_title', '').upper()
            title_w = draw.textlength(title_text, font=font_title)
            title_x = (width - title_w) // 2
            # Drop shadow
            draw.text((title_x + 3, 43), title_text, font=font_title, fill="black")
            draw.text((title_x, 40), title_text, font=font_title, fill="#e8e8e8")
            
            # Draw Date and Time Center Stacked
            font_time = ImageFont.truetype(f_bold, 70)
            # PSD: Sentence Case for Day (Strict Cleanup for v20 Ghost Char Issue)
            day_raw = data.get('day', '')
            # Filter non-printable/hidden characters that might cause ghost dots
            day_text_clean = "".join(c for c in day_raw if c.isprintable()).strip()
            # Special case for Turkish 'i' to 'İ' etc might happen but capitalize() is safer here
            day_text = day_text_clean.capitalize() if day_text_clean else ""
            hour_text = data.get('hour', '').strip()
            
            day_w = draw.textlength(day_text, font=font_time)
            hour_w = draw.textlength(hour_text, font=font_time)
            
            # DAY in UEFA ENERGY GREEN (#06BF50)
            draw.text(((width - day_w) // 2, 130), day_text, font=font_time, fill="#06BF50")
            
            # HOUR in WHITE
            draw.text(((width - hour_w) // 2, 220), hour_text, font=font_time, fill="#FFFFFF")
            
            # UEFA Logo (FAITHFUL SCALE v20: 110px Height)
            logo_path = self.assets_path / "branding" / "uefa_logo.png"
            if logo_path.exists():
                logo_img = Image.open(logo_path).convert("RGBA")
                l_w, l_h = logo_img.size
                target_h = 110
                target_w = int(target_h * (l_w / l_h))
                logo_img = logo_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                # Vertical Positioning: 330px Top (Middle area)
                canvas.alpha_composite(logo_img, ((width - target_w) // 2, 330))
            
            # Special UEFA Nesine Box (Exact PSD-1 bottom position)
            self.draw_nesine_uefa_box(canvas, (492, 536), width=217, height=93)
            
            # UEFA Hemen Oyna (Refined v12 spacing - between logo and box)
            ho_path = self.assets_path / "branding" / "hemen_oyna.png"
            if ho_path.exists():
                ho_img = Image.open(ho_path).convert("RGBA").resize((185, 52), Image.Resampling.LANCZOS)
                canvas.alpha_composite(ho_img, ((width - 185) // 2, 480))

        else:
            # --- Ziraat Layout: Teams Left Center, Time Right Center ---
            # Fontlar (Monument Extended) - Okunabilirlik için boyutlar optimize edildi
            font_teams = ImageFont.truetype(f_bold, 58) # 75 çok büyüktü
            font_info = ImageFont.truetype(f_reg, 32)
            font_time = ImageFont.truetype(f_reg, 48)

            v_teams = self.master["variables"]["team_names_1"]
            target_team_w = 440 
            center_x = v_teams["left"] + v_teams["width"] // 2
            
            # Dikey ayrımı artırıyoruz (+/- 55px)
            self.draw_text_with_spacing(draw, data['team_1'].upper(), (center_x - target_team_w//2, v_teams["top"] - 55), font_teams, fill="black", target_width=target_team_w)
            self.draw_text_with_spacing(draw, data['team_2'].upper(), (center_x - target_team_w//2, v_teams["top"] + 55), font_teams, fill="black", target_width=target_team_w)

            v_info = next(c for c in self.master["constants"] if "gün_saat" in c["name"].lower())
            target_info_w = 240
            info_center_x = v_info["left"] + v_info["width"] // 2
            
            self.draw_text_with_spacing(draw, data['hour'].upper(), (info_center_x - target_info_w//2, v_info["top"] - 15), font_time, fill="black", target_width=target_info_w)
            self.draw_text_with_spacing(draw, data['day'].upper(), (info_center_x - target_info_w//2, v_info["top"] + 25), font_info, fill="black", target_width=target_info_w)

        return canvas

    def generate_120x600(self, data, league="ZIRAAT"):
        width, height = 120, 600
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Lig bazlı Branding
        if league.upper() == "UEFA":
            logo_path = os.path.join(self.assets_path, "branding", "uefa_logo.png")
            f_bold = self.fonts["uefa_bold"]
            f_reg = self.fonts["uefa_reg"]
        else:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "ztk_yatay_logo.png")
            f_bold = self.fonts["ziraat_bold"]
            f_reg = self.fonts["ziraat_reg"]
        
        bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_120x600_clean.png"
        if os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGBA")
            canvas.paste(bg, (0, 0))
        else:
            canvas.paste((214, 0, 28, 255), [0, 0, width, height])

        if os.path.exists(logo_path):
            img = Image.open(logo_path).convert("RGBA")
            # UEFA dikey bir logo, Ziraat yatay. Boyutlandırmayı lig tipine göre ayarlıyoruz.
            if league.upper() == "UEFA":
                img.thumbnail((100, 140), Image.Resampling.LANCZOS)
                canvas.paste(img, (60 - img.size[0]//2, 20), img)
            else:
                img = img.resize((100, 32), Image.Resampling.LANCZOS)
                canvas.paste(img, (10, 30), img)

        p_y = 163
        for i in [1, 2]:
            p_img_path = data.get(f"player_{i}_path")
            p_x = 2 if i == 1 else 61
            p_size = (57, 77)
            team_name = data.get(f"team_{i}")
            t_colors = self.get_team_colors(team_name)
            
            # Procedural Backdrop (Scale down)
            b_size = (57, 77)
            b_final = self.draw_procedural_backdrop(t_colors, b_size).resize((b_size[0]+4, b_size[1]+4))
            canvas.alpha_composite(b_final, (p_x - 2, p_y - 2))
            
            if p_img_path and os.path.exists(p_img_path):
                p_img_source = Image.open(p_img_path).convert("RGBA")
                pop_out = 0 # Dikeyde kafa dışarıda değil, temiz kesim
                p_img = ImageOps.fit(p_img_source, p_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                p_mask = self.create_player_mask(p_size, radius=20)
                p_final = Image.new("RGBA", p_size, (0,0,0,0))
                p_final.paste(p_img, (0, 0), p_mask)
                canvas.alpha_composite(p_final, (p_x, p_y))

        l_y = 229
        for i in [1, 2]:
            l_path = data.get(f"logo_{i}_path")
            l_x = 13 if i == 1 else 69
            l_size = (36, 42) if i == 1 else (43, 43)
            if l_path and os.path.exists(l_path):
                l_img = Image.open(l_path).convert("RGBA").resize(l_size)
                canvas.paste(l_img, (l_x, l_y), l_img)

        draw = ImageDraw.Draw(canvas)
        font_teams = ImageFont.truetype(f_bold, 16)
        font_info = ImageFont.truetype(f_reg, 12)
        font_time = ImageFont.truetype(f_reg, 18)

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

    def generate_320x100(self, data, league="ZIRAAT"):
        """3 sahneli 320x100 GIF banner üretir."""
        width, height = 320, 100
        
        # Lig bazlı Branding
        if league.upper() == "UEFA":
            logo_path = os.path.join(self.assets_path, "branding", "uefa_logo.png")
            f_bold = self.fonts["uefa_bold"]
            f_reg = self.fonts["uefa_reg"]
        else:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "ztk_yatay_logo.png")
            f_bold = self.fonts["ziraat_bold"]
            f_reg = self.fonts["ziraat_reg"]

        bg_path = os.path.join(os.path.dirname(__file__), "..", "bg_320x100_clean.png")
        
        rgb_frames = []
        
        # --- SAHNE 1 ---
        from PIL import ImageEnhance
        base_bg = Image.open(bg_path).convert("RGBA")
        enhancer = ImageEnhance.Contrast(base_bg)
        frame1 = enhancer.enhance(1.1) 
        
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
            team_name = data.get(f"team_{i}")
            t_colors = self.get_team_colors(team_name)
            
            # Procedural Backdrop (GIF Scale)
            b_size = (p_size[0], p_size[1])
            b_final = self.draw_procedural_backdrop(t_colors, b_size).resize((b_size[0]+4, b_size[1]+4))
            frame2.alpha_composite(b_final, (px - 2, py - 2))
            
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
            font_main = ImageFont.truetype(f_bold, 15)
            font_sub = ImageFont.truetype(f_reg, 13)
            
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

    def generate_300x50(self, data, league="ZIRAAT"):
        """Ziraat 3-sahne 300x50 GIF üretir."""
        width, height = 300, 50
        tpl_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates"
        
        # Lig bazlı Branding
        if league.upper() == "UEFA":
            logo_path = os.path.join(self.assets_path, "branding", "uefa_logo.png")
            f_bold = self.fonts["uefa_bold"]
            f_reg = self.fonts["uefa_reg"]
        else:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "ztk_yatay_logo.png")
            f_bold = self.fonts["ziraat_bold"]
            f_reg = self.fonts["ziraat_reg"]
        
        rgb_frames = []
        
        # --- ORTAK BILESENLER (Static) ---
        bg_path = os.path.join(tpl_path, "bg_300x50_clean.png")
        if not os.path.exists(bg_path):
            bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_320x100_clean.png"
            
        bant_path = os.path.join(tpl_path, "nesine_300x50_bant.png")
        ho_path = os.path.join(tpl_path, "hemen_oyna_300x50.png")
        
        def create_base_frame():
            f = Image.open(bg_path).convert("RGBA").resize((width, height))
            if os.path.exists(bant_path):
                bant = Image.open(bant_path).convert("RGBA")
                f.paste(bant, (-18, -2), bant)
            if os.path.exists(ho_path):
                ho = Image.open(ho_path).convert("RGBA")
                f.paste(ho, (233, 16), ho)
            return f

        # --- SAHNE 1 (Logo) ---
        frame1 = create_base_frame()
        if os.path.exists(logo_path):
            z_img = Image.open(logo_path).convert("RGBA").resize((130, 42), Image.Resampling.LANCZOS)
            frame1.paste(z_img, (83, 4), z_img)
        rgb_frames.append(frame1.convert("RGB"))
        
        # --- SAHNE 2 (Oyuncular & Logolar) ---
        frame2 = create_base_frame()
        # Oyuncu 1 & Logo 1
        p1_path = data.get("player_1_path")
        if p1_path and os.path.exists(p1_path):
            p1 = Image.open(p1_path).convert("RGBA")
            p1 = ImageOps.fit(p1, (35, 48), centering=(0.5, 0.0))
            frame2.paste(p1, (81, 0), p1)
        l1_path = data.get("logo_1_path")
        if l1_path and os.path.exists(l1_path):
            l1 = Image.open(l1_path).convert("RGBA").resize((29, 36), Image.Resampling.LANCZOS)
            frame2.paste(l1, (114, 10), l1)
            
        # Oyuncu 2 & Logo 2
        p2_path = data.get("player_2_path")
        if p2_path and os.path.exists(p2_path):
            p2 = Image.open(p2_path).convert("RGBA")
            p2 = ImageOps.fit(p2, (35, 47), centering=(0.5, 0.0))
            frame2.paste(p2, (181, 1), p2)
        l2_path = data.get("logo_2_path")
        if l2_path and os.path.exists(l2_path):
            l2 = Image.open(l2_path).convert("RGBA").resize((33, 36), Image.Resampling.LANCZOS)
            frame2.paste(l2, (157, 10), l2)
        rgb_frames.append(frame2.convert("RGB"))
        
        # --- SAHNE 3 (Takım Isimleri & Saat) ---
        frame3 = create_base_frame()
        draw3 = ImageDraw.Draw(frame3)
        try:
            font_details = ImageFont.truetype(f_bold, 28)
            font_oyna = ImageFont.truetype(f_bold, 20)
            
            t1 = data.get("team_1", "").upper()
            t2 = data.get("team_2", "").upper()
            day_txt = data.get('day', '').upper()
            hour_txt = data.get('hour', '')
            
            # Orta alan boundaries
            # Nesine bandı x=50, Hemen Oyna x=233
            
            # Takım isimleri - Sol taraf (alt alta)
            draw3.text((58, 10), t1, font=f_bold, fill="black")
            draw3.text((58, 28), t2, font=f_bold, fill="black")
            
            # Gün/Saat - Sağ taraf (alt alta, sağa yaslı)
            # Sağ sınır olarak Hemen Oyna'nın başladığı yerin biraz öncesini alıyoruz
            safe_right = 228
            
            day_box = draw3.textbbox((0, 0), day_txt, font=f_sub)
            day_w = day_box[2] - day_box[0]
            draw3.text((safe_right - day_w, 12), day_txt, font=f_sub, fill="black")
            
            hour_box = draw3.textbbox((0, 0), hour_txt, font=f_sub)
            hour_w = hour_box[2] - hour_box[0]
            draw3.text((safe_right - hour_w, 28), hour_txt, font=f_sub, fill="black")
        except:
            pass
        rgb_frames.append(frame3.convert("RGB"))
        
        # GIF Olarak Kaydet
        gif_path = "/tmp/ziraat_300x50.gif"
        rgb_frames[0].save(
            gif_path,
            save_all=True,
            append_images=rgb_frames[1:],
            duration=1500,
            loop=0,
            optimize=True
        )
        return gif_path

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

if __name__ == "__main__":
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
