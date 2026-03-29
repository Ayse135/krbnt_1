import os
import json
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from pathlib import Path
from core.vision_utils import VisionUtils

class BannerEngine:
    def __init__(self, master_prompt_path, assets_base_path, fonts_path=None):
        with open(master_prompt_path, "r", encoding="utf-8") as f:
            self.master = json.load(f)
        
        self.assets_path = Path(assets_base_path)
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

    def get_team_colors(self, team_name):
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

    def apply_glow(self, img, color=(6, 191, 80), radius=55, opacity=220):
        """Creates a high-power 'High-Voltage' Aura with dual-core density (v22)."""
        padding = radius * 3
        padded_size = (img.width + padding * 2, img.height + padding * 2)
        expanded_img = Image.new("RGBA", padded_size, (0, 0, 0, 0))
        expanded_img.paste(img, (padding, padding))
        mask = expanded_img.split()[-1]
        dilated_mask = mask.filter(ImageFilter.MaxFilter(size=9))
        glow_color_img = Image.new("RGBA", padded_size, color + (opacity,))
        aura_glow = Image.new("RGBA", padded_size, (0,0,0,0))
        aura_glow.paste(glow_color_img, (0,0), dilated_mask)
        aura_glow = aura_glow.filter(ImageFilter.GaussianBlur(radius))
        core_radius = max(10, radius // 3)
        core_glow = Image.new("RGBA", padded_size, (0,0,0,0))
        core_glow.paste(glow_color_img, (0,0), dilated_mask)
        core_glow = core_glow.filter(ImageFilter.GaussianBlur(core_radius))
        power_composite = Image.new("RGBA", padded_size, (0,0,0,0))
        power_composite.alpha_composite(aura_glow); power_composite.alpha_composite(core_glow)
        power_composite.alpha_composite(core_glow); power_composite.alpha_composite(aura_glow)
        final = Image.new("RGBA", padded_size, (0,0,0,0))
        final.alpha_composite(power_composite); final.alpha_composite(expanded_img)
        return final

    def draw_nesine_uefa_box(self, canvas, pos, width=217, height=93):
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([pos[0], pos[1], pos[0] + width, pos[1] + height], fill="#FFCC00")
        n_path = self.assets_path / "branding" / "nesine_logo.png"
        if n_path.exists():
            n_img = Image.open(n_path).convert("RGBA")
            n_w, n_h = 141, 68
            n_img = ImageOps.fit(n_img, (n_w, n_h), method=Image.Resampling.LANCZOS)
            canvas.paste(n_img, (pos[0] + (width - n_w) // 2, pos[1] + 12), n_img)

    def create_player_mask(self, size, radius=130):
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        w, h = size
        r = min(radius, w // 2, h // 2)
        draw.rectangle([0, r, w, h], fill=255)
        draw.rectangle([r, 0, w, r], fill=255)
        draw.pieslice([0, 0, 2*r, 2*r], 180, 270, fill=255)
        return mask

    def draw_radial_glow(self, size, color):
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
        b_canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        mask = self.create_player_mask(size, radius=180)
        base = Image.new("RGBA", size, t_colors["p"])
        glow = self.draw_radial_glow(size, (255, 255, 255))
        base.alpha_composite(glow)
        wave_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates/backdrop_waves_v3.png"
        if os.path.exists(wave_path):
            waves = Image.open(wave_path).convert("L").resize(size, Image.Resampling.LANCZOS)
            wave_overlay = Image.new("RGBA", size, (255, 255, 255, 40))
            base.paste(wave_overlay, (0, 0), waves)
        b_canvas.paste(base, (0, 0), mask)
        outline_mask = self.create_player_mask((size[0]+20, size[1]+20), radius=190)
        outline_img = Image.new("RGBA", (size[0]+20, size[1]+20), t_colors["s"])
        final_b = Image.new("RGBA", (size[0]+20, size[1]+20), (0, 0, 0, 0))
        final_b.paste(outline_img, (0, 0), outline_mask)
        final_b.alpha_composite(b_canvas, (10, 10))
        return final_b

    def draw_text_with_spacing(self, draw, text, position, font, fill="white", spacing=0, target_width=None):
        x, y = position
        current_x = x
        if target_width:
            total_chars_width = sum(draw.textlength(c, font=font) for c in text)
            if len(text) > 1: spacing = (target_width - total_chars_width) / (len(text) - 1)
        for char in text:
            draw.text((current_x, y), char, font=font, fill=fill)
            current_x += draw.textlength(char, font=font) + spacing

    def generate_1200x628(self, data, league="ZIRAAT"):
        width, height = self.master["size"]["width"], self.master["size"]["height"]
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        template_dir = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates"
        
        if league.upper() == "UEFA":
            canvas.paste((0, 0, 0, 255), [0, 0, width, height])
            f_bold = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_SemiExpanded-Bold.ttf"
        else:
            f_bold = self.fonts["ziraat_bold"]
            bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_ultra_clean.png"
            if os.path.exists(bg_path):
                bg = Image.open(bg_path).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
                canvas.paste(bg, (0, 0))

        # Player Loop
        if league.upper() == "UEFA":
            uefa_head_anchors = [(180, 250), (1020, 250)]
            for i in [1, 2]:
                p_path = data.get(f"player_{i}_path")
                if p_path and os.path.exists(p_path):
                    p_img = Image.open(p_path).convert("RGBA")
                    # Auto-Aimer v23
                    p_final, paste_pos = VisionUtils.align_player_to_anchor(p_img, uefa_head_anchors[i-1], target_face_h=190)
                    radius = 45
                    p_glow = self.apply_glow(p_final, color=(6, 191, 80), radius=radius, opacity=200)
                    canvas.alpha_composite(p_glow, (paste_pos[0] - radius*3, paste_pos[1] - radius*3))
        else:
            for i in [1, 2]:
                v_player = self.master["variables"].get(f"player_{i}")
                p_path = data.get(f"player_{i}_path")
                if v_player and p_path and os.path.exists(p_path):
                    t_colors = self.get_team_colors(data.get(f"team_{i}", ""))
                    b_size = (380, 480)
                    b_final = self.draw_procedural_backdrop(t_colors, b_size)
                    canvas.alpha_composite(b_final, (v_player["left"] + (v_player["width"] - b_size[0]) // 2 - 10, v_player["top"] + 50))
                    p_src = Image.open(p_path).convert("RGBA")
                    p_full_size = (v_player["width"], v_player["height"] + 140)
                    p_img = ImageOps.fit(p_src, p_full_size, centering=(0.5, 0.0))
                    p_mask = Image.new("L", p_full_size, 0)
                    p_mask.paste(self.create_player_mask((v_player["width"], v_player["height"]), radius=130), (0, 140))
                    p_mask.paste(255, [0, 0, v_player["width"], 140])
                    p_final = Image.new("RGBA", p_full_size, (0,0,0,0))
                    p_final.paste(p_img, (0, 0), p_mask)
                    canvas.alpha_composite(p_final, (v_player["left"], v_player["top"] - 140))

        # Logo Loop
        if league.upper() == "UEFA":
            uefa_logo_centers = [(288, 305), (1110, 305)]
            for i in [1, 2]:
                l_path = data.get(f"logo_{i}_path")
                if l_path and os.path.exists(l_path):
                    l_img = Image.open(l_path).convert("RGBA").resize((120, 120))
                    l_glow = self.apply_glow(l_img, color=(6, 191, 80), radius=50, opacity=220)
                    canvas.alpha_composite(l_glow, (uefa_logo_centers[i-1][0] - 150, uefa_logo_centers[i-1][1] - 150))
                    canvas.alpha_composite(l_img, (uefa_logo_centers[i-1][0] - 60, uefa_logo_centers[i-1][1] - 60))
            
            # Branding & Text
            draw = ImageDraw.Draw(canvas)
            font_title = ImageFont.truetype(f_bold, 55)
            title = data.get('match_title', '').upper()
            tw = draw.textlength(title, font=font_title)
            draw.text(((width-tw)//2+3, 43), title, font=font_title, fill="black")
            draw.text(((width-tw)//2, 40), title, font=font_title, fill="#e8e8e8")
            
            font_time = ImageFont.truetype(f_bold, 70)
            day_text = "".join(c for c in data.get('day','').strip() if c.isprintable()).capitalize()
            hour_text = data.get('hour', '').strip()
            dw, hw = draw.textlength(day_text, font=font_time), draw.textlength(hour_text, font=font_time)
            draw.text(((width-dw)//2, 130), day_text, font=font_time, fill="#06BF50")
            draw.text(((width-hw)//2, 220), hour_text, font=font_time, fill="white")
            
            u_path = self.assets_path / "branding" / "uefa_logo.png"
            if u_path.exists():
                u_img = Image.open(u_path).convert("RGBA")
                uw, uh = u_img.size; th=110; tw=int(th*(uw/uh))
                canvas.alpha_composite(u_img.resize((tw, th)), ((width-tw)//2, 330))
            self.draw_nesine_uefa_box(canvas, (492, 536))
            ho_path = self.assets_path / "branding" / "hemen_oyna.png"
            if ho_path.exists(): canvas.alpha_composite(Image.open(ho_path).convert("RGBA").resize((185, 52)), ((width-185)//2, 480))
            
            
            # Player Signatures (Absolute Top)
            for i in [1, 2]:
                sig_path = data.get(f"signature_{i}_path")
                if sig_path and os.path.exists(sig_path):
                    sig_img = Image.open(sig_path).convert("RGBA")
                    # Scale signature to reasonable size (e.g. 300px width)
                    sig_img.thumbnail((300, 180), Image.Resampling.LANCZOS)
                    # Positions: Bottom Left and Bottom Right areas
                    sig_pos = (20, 420) if i == 1 else (width - sig_img.width - 20, 420)
                    canvas.alpha_composite(sig_img, sig_pos)
        else:
            # Ziraat Branding / Text Logic
            pass

        return canvas

    def generate_120x600(self, data, league="ZIRAAT"): return Image.new("RGBA", (120, 600))
    def generate_320x100(self, data, league="ZIRAAT"): return "path/to/gif"
    def generate_300x50(self, data, league="ZIRAAT"): return "path/to/gif"

if __name__ == "__main__":
    ENGINE = BannerEngine("/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat/1200x628_master.json", "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets")
    # Add test call here
