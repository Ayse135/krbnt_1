import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from ..base import BaseLayout

class UEFA1200(BaseLayout):
    def render(self, data):
        """PSD-Perfect UEFA 1200x628 Replication (Balanced Players & Logos)."""
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

        # 3. Akıllı Oyuncu Yerleşimi (Tight Halo Glow)
        # PSD OyuncularYeni Bbox: Left (-78, 133), Right (779, 131)
        p1_scale = self.overrides.get("player_1_scale", self.overrides.get("player_scale", 1.0))
        p2_scale = self.overrides.get("player_2_scale", self.overrides.get("player_scale", 1.0))
        
        players_data = [
            {
                "path": data.get("player_1_path"), 
                "center_x": 172 + int(self.overrides.get("player_1_x_offset", 0)), 
                "target_y": 133 + int(self.overrides.get("player_1_y_offset", 0)), 
                "scale_adj": p1_scale
            },
            {
                "path": data.get("player_2_path"), 
                "center_x": 1037 + int(self.overrides.get("player_2_x_offset", 0)), 
                "target_y": 131 + int(self.overrides.get("player_2_y_offset", 0)), 
                "scale_adj": p2_scale
            }
        ]

        for p in players_data:
            if p["path"] and os.path.exists(p["path"]):
                p_img = Image.open(p["path"]).convert("RGBA")
                self.smart_position_player(canvas, p_img, p["center_x"], p["target_y"], p.get("scale_adj", 1.0))

        # 4. Takım Logoları (Geniş Atmosferik Işıma)
        # PSD Logolar: Left (347, 225), Right (850, 229)
        l_y_override = self.overrides.get("logo_y", 225)
        l_y_off = int(self.overrides.get("logo_y_offset", 0))
        
        logos_data = [
            {
                "path": data.get("logo_1_path"), 
                "center": (347 + int(self.overrides.get("logo_1_x_offset", 0)), l_y_override + l_y_off), 
                "max_size": (int(185 * float(self.overrides.get("logo_1_scale", 1.0))), int(210 * float(self.overrides.get("logo_1_scale", 1.0))))
            },
            {
                "path": data.get("logo_2_path"), 
                "center": (850 + int(self.overrides.get("logo_2_x_offset", 0)), l_y_override + 4 + l_y_off), 
                "max_size": (int(175 * float(self.overrides.get("logo_2_scale", 1.0))), int(210 * float(self.overrides.get("logo_2_scale", 1.0))))
            }
        ]

        for l in logos_data:
            if l["path"] and os.path.exists(l["path"]):
                l_img = Image.open(l["path"]).convert("RGBA")
                l_img.thumbnail(l["max_size"], Image.Resampling.LANCZOS)
                # Logos: Wide Spread (Dilation=35, Blur=65)
                self.draw_mask_glow(canvas, l_img, l["center"], color=(6, 191, 80, 220), dilation=35, blur=65)
                canvas.alpha_composite(l_img, (l["center"][0] - l_img.width // 2, l["center"][1] - l_img.height // 2))

        # 5. Yazılar (Dynamic Title & Space Refinement)
        try:
            title = data.get('match_title', '').upper()
            f_saira_cond = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
            
            if title:
                # Dinamik başlık çizimi: match_title_y (absolute) or match_title_y_offset
                t_y = self.overrides.get("match_title_y", self.overrides.get("title_y", 30)) + int(self.overrides.get("match_title_y_offset", 0))
                self.draw_dynamic_title(draw, title, f_saira_cond, max_width=1000, start_y=t_y)
            
            # Day & Hour: Positional and FS Control
            day_text = data.get('day', 'Pazartesi').capitalize()
            hour_text = data.get('hour', '20:30')
            
            fs_info = self.overrides.get("match_info_fs", 88)
            font_info = ImageFont.truetype(f_saira_cond, fs_info)
            
            dy_off = int(self.overrides.get("day_y_offset", 0))
            hy_off = int(self.overrides.get("hour_y_offset", 0))
            info_y_off = int(self.overrides.get("match_info_y_offset", 0))

            day_y = self.overrides.get("day_y", 130) + dy_off + info_y_off
            hour_y = self.overrides.get("hour_y", 205) + hy_off + info_y_off
            
            draw.text(((width - draw.textlength(day_text, font=font_info)) // 2, day_y), day_text, font=font_info, fill="#06BF50")
            draw.text(((width - draw.textlength(hour_text, font=font_info)) // 2, hour_y), hour_text, font=font_info, fill="white")
        except Exception as e:
            print(f"Typo Error: {e}")

        # 6. Branding (UEFA Logo & Hemen Oyna)
        if os.path.exists(u_logo_path):
            u_img = Image.open(u_logo_path).convert("RGBA")
            u_img = u_img.resize((81, 124), Image.Resampling.LANCZOS)
            u_y = self.overrides.get("uefa_logo_y", 323)
            canvas.alpha_composite(u_img, ((width - u_img.width) // 2, u_y))

        ho_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/hemen_oyna.png"
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA")
            ho_img = ho_img.resize((190, 59), Image.Resampling.LANCZOS)
            ho_y = self.overrides.get("hemen_oyna_y", 465)
            canvas.alpha_composite(ho_img, (506, ho_y))

        draw.rectangle([492, 536, 492 + 217, 536 + 93], fill=(252, 215, 0))
        n_logo_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/nesine_logo.png"
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((180, 70), Image.Resampling.LANCZOS)
            canvas.alpha_composite(n_img, (492 + (217 - n_img.width) // 2, 536 + (93 - n_img.height) // 2))

        # 7. Save Output
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_uefa_1200.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        canvas.save(out_path)
        return out_path

    def smart_position_player(self, canvas, img, center_x, target_y, scale_adj=1.0):
        """Oyuncuyu kafa/omuz hattına göre akıllıca ölçekler ve yerleştirir."""
        # 1. Kafa Analizi
        alpha = img.split()[3]
        bbox = alpha.getbbox() 
        if not bbox: return
        
        # Oyuncuyu PSD standardına göre ölçekle
        current_height = bbox[3] - bbox[1]
        target_render_height = 800 * scale_adj
        scale = target_render_height / current_height
        
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Yeni merkez ve kafa konumu
        new_alpha = img.split()[3]
        new_bbox = new_alpha.getbbox()
        
        # Player Glow: Tight Halo (Dilation=8, Blur=25, opacity=180)
        self.draw_mask_glow(canvas, img, (center_x, target_y + (new_h/2) - (new_bbox[1])), 
                            color=(6, 191, 80, 180), dilation=8, blur=25)
        
        # Yerleştir
        render_x = center_x - (new_w // 2)
        render_y = target_y - new_bbox[1]
        canvas.alpha_composite(img, (int(render_x), int(render_y)))

    def draw_dynamic_title(self, draw, text, font_path, max_width, start_y):
        """Metni genişliğe göre böler, gerekirse küçültür ve ortalı şekilde çizer."""
        base_size = 65
        padding = 10
        width = 1200
        
        # 1. Metni bölme (Kelimelere göre)
        words = text.split()
        lines = []
        current_line = []
        
        font = ImageFont.truetype(font_path, base_size)
        
        for word in words:
            test_line = " ".join(current_line + [word])
            if draw.textlength(test_line, font=font) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Tek bir kelime bile sığmıyorsa (çok uzun kelime), zorla kes
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(" ".join(current_line))
            
        # 2. Eğer 2 satırdan fazlaysa veya sığmıyorsa fontu küçült
        while (len(lines) > 2 or any(draw.textlength(line, font=font) > max_width for line in lines)) and base_size > 30:
            base_size -= 5
            font = ImageFont.truetype(font_path, base_size)
            # Metni yeni boyutla tekrar böl (opsiyonel ama daha doğru)
            lines = []
            current_line = []
            for word in words:
                test_line = " ".join(current_line + [word])
                if draw.textlength(test_line, font=font) <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
            if current_line: lines.append(" ".join(current_line))

        # 3. Çizim
        current_y = start_y
        for line in lines[:2]: # Maksimum 2 satır
            w_line = draw.textlength(line, font=font)
            draw.text(((width - w_line) // 2, current_y), line, font=font, fill="white")
            current_y += base_size + padding

    def draw_mask_glow(self, canvas, img, center, color, dilation=15, blur=30):
        """Logonun/Oyuncunun çevresini saran konfigüre edilebilir neon hale efekti."""
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        margin = blur + 50
        glow_canvas = Image.new("RGBA", (img.width + margin*2, img.height + margin*2), (0,0,0,0))
        
        alpha = img.split()[3]
        
        # MaxFilter boyutu her zaman TEK (ODD) sayı olmalıdır.
        def force_odd(n):
            n = int(n)
            return n if n % 2 != 0 else n + 1

        # Dış Işıma (Genişlik kontrolü: dilation ve blur)
        ambient_mask = alpha.filter(ImageFilter.MaxFilter(force_odd(dilation)))
        outer_glow = Image.merge("RGBA", (
            Image.new("L", img.size, color[0]), Image.new("L", img.size, color[1]), Image.new("L", img.size, color[2]),
            ambient_mask
        ))
        
        # İç Işıma (Daha sıkı)
        inner_mask = alpha.filter(ImageFilter.MaxFilter(force_odd(dilation//2 + 2)))
        inner_glow = Image.merge("RGBA", (
            Image.new("L", img.size, color[0]), Image.new("L", img.size, color[1]), Image.new("L", img.size, color[2]),
            inner_mask
        ))
        
        glow_canvas.paste(outer_glow, (margin, margin), outer_glow)
        glow_canvas = glow_canvas.filter(ImageFilter.GaussianBlur(blur))
        
        inner_layer = Image.new("RGBA", glow_canvas.size, (0,0,0,0))
        inner_layer.paste(inner_glow, (margin, margin), inner_glow)
        inner_layer = inner_layer.filter(ImageFilter.GaussianBlur(int(blur/3) + 1))
        
        glow_canvas.alpha_composite(inner_layer)
        r, g, b, a = glow_canvas.split()
        a = a.point(lambda i: int(i * (color[3]/150.0))) 
        glow_canvas = Image.merge("RGBA", (r, g, b, a))
        
        canvas.alpha_composite(glow_canvas, (int(center[0] - glow_canvas.width//2), int(center[1] - glow_canvas.height//2)))

    def draw_glow(self, canvas, pos, radius, color):
        """Legacy radial glow."""
        pass
