import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageMath, ImageChops
from ..base import BaseLayout

class UEFA120_600(BaseLayout):
    def render(self, data):
        """UEFA 120x600 Vertical PNG Banner with Supersampling (2x)."""
        sw, sh = 120, 600
        scale = 2
        width, height = sw * scale, sh * scale
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(canvas)
        
        # 1. Config & Assets
        f_title = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat/MonumentExtended-Ultrabold.otf"
        f_saira_cond = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        u_logo_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/uefa_logo.png"
        
        # 2. Background: 100% Pure Black + Custom Top Overlay
        canvas.paste((0, 0, 0, 255), [0, 0, width, height])
        
        # Load and paste the custom top background (120x600_bg_ust.png)
        top_bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/120x600_png/120x600_bg_ust.png"
        if os.path.exists(top_bg_path):
            top_bg = Image.open(top_bg_path).convert("RGBA")
            top_bg = top_bg.resize((width, height), Image.Resampling.LANCZOS)
            canvas.alpha_composite(top_bg, (0, 0))
            
        # Load and paste the custom bottom background (120x600_bg_alt.png)
        bot_bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/120x600_png/120x600_bg_alt.png"
        if os.path.exists(bot_bg_path):
            bot_bg = Image.open(bot_bg_path).convert("RGBA")
            bot_bg = bot_bg.resize((width, height), Image.Resampling.LANCZOS)
            # Pasted over top/black since it's also 120x600 and likely semi-transparent
            canvas.alpha_composite(bot_bg, (0, 0))

        # 3. Match Title (Wrapped into 3 lines) - Target Y: 25
        try:
            title = data.get('match_title', '').upper()
            if title:
                # Reduced base size from 14 to 11 for better 120px width support
                base_fs = 11
                font_title = ImageFont.truetype(f_title, base_fs * scale)
                words = title.split()
                lines = []
                current_line = []
                
                # Wrapping logic
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if draw.textlength(test_line, font=font_title) < 100 * scale:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                lines.append(' '.join(current_line))
                
                # Auto-scaling loop for extremely long words
                while any(draw.textlength(l, font=font_title) > 105 * scale for l in lines) and base_fs > 7:
                    base_fs -= 0.5
                    font_title = ImageFont.truetype(f_title, int(base_fs * scale))
                
                curr_y = 25 * scale
                for line in lines[:3]:
                    w_l = draw.textlength(line, font=font_title)
                    draw.text(((width - w_l) // 2, curr_y), line, font=font_title, fill="white")
                    curr_y += (base_fs + 4) * scale
        except Exception as e:
            print(f"Title Error: {e}")

        # 4. Team Logos (Side-by-Side at y=140)
        # Using the new "Power Glow" logic for high visibility
        logos_data = [
            {"path": data.get("logo_1_path"), "center": (35 * scale, 140 * scale), "size": (48 * scale, 58 * scale)},
            {"path": data.get("logo_2_path"), "center": (85 * scale, 140 * scale), "size": (48 * scale, 58 * scale)}
        ]
        for l in logos_data:
            if l["path"] and os.path.exists(l["path"]):
                l_img = Image.open(l["path"]).convert("RGBA")
                l_img.thumbnail(l["size"], Image.Resampling.LANCZOS)
                # Refined logo glow (Reduced intensity and reach)
                self.draw_mask_glow(canvas, l_img, l["center"], color=(6, 191, 80, 255), dilation=4 * scale, blur=16 * scale, intensity=2.2)
                canvas.alpha_composite(l_img, (int(l["center"][0] - l_img.width // 2), int(l["center"][1] - l_img.height // 2)))

        # 5. Match Info (Day Green, Hour White) - Centered between Logos (y=169) and UEFA (y=252)
        try:
            day_text = data.get('day', 'Pazartesi').capitalize()
            hour_text = data.get('hour', '20:30')
            font_info = ImageFont.truetype(f_saira_cond, 30 * scale)
            
            # Precisely centered in the available ~80px gap
            draw.text((60 * scale, 195 * scale), day_text, font=font_info, fill="#06BF50", anchor="mm")
            draw.text((60 * scale, 225 * scale), hour_text, font=font_info, fill="white", anchor="mm")
        except Exception as e:
            print(f"Info Error: {e}")

        # 6. UEFA Logo (Moved to 1x Post-Processing)
        pass

        # 7. Akıllı Oyuncu Yerleşimi (Heads at y=324)
        players_data = [
            {"path": data.get("player_1_path"), "center_x": 40 * scale, "target_y": 324 * scale},
            {"path": data.get("player_2_path"), "center_x": 80 * scale, "target_y": 340 * scale}
        ]
        for p in players_data:
            if p["path"] and os.path.exists(p["path"]):
                p_img = Image.open(p["path"]).convert("RGBA")
                self.smart_position_player(canvas, p_img, p["center_x"], p["target_y"], scale)

        # 8. Branding (Moved to 1x post-process)
        pass

        # 10. Post-Processing: Downsample & Sharpen
        final_canvas = canvas.resize((sw, sh), Image.Resampling.LANCZOS)
        final_canvas = final_canvas.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
        
        # 11. Add Branding at 1x resolution for maximum sharpness
        draw_1x = ImageDraw.Draw(final_canvas)
        
        # A. UEFA Logo (y=252)
        if os.path.exists(u_logo_path):
            u_img = Image.open(u_logo_path).convert("RGBA")
            u_img.thumbnail((50, 70), Image.Resampling.LANCZOS)
            final_canvas.alpha_composite(u_img, ((sw - u_img.width) // 2, 252))
            
        # B. Hemen Oyna (y=492)
        ho_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/hemen_oyna.png"
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA")
            ho_img.thumbnail((104, 33), Image.Resampling.LANCZOS)
            final_canvas.alpha_composite(ho_img, ((sw - ho_img.width) // 2, 492))
            
        # C. Nesine Footer (y=540)
        draw_1x.rectangle([0, 540, sw, 600], fill=(252, 215, 0))
        n_logo_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/nesine_logo.png"
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((100, 50), Image.Resampling.LANCZOS)
            final_canvas.alpha_composite(n_img, ((sw - n_img.width) // 2, int(540 + (60 - n_img.height) // 2)))

        # 11. Save Output
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_uefa_120_600.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        final_canvas.save(out_path)
        return out_path

    def smart_position_player(self, canvas, img, center_x, target_y, scale):
        """Dikey banner için oyuncu yerleşimi (Daha küçük ölçekli)."""
        alpha = img.split()[3]
        bbox = alpha.getbbox()
        if not bbox: return
        
        current_height = bbox[3] - bbox[1]
        target_render_height = 250 * scale
        scaling_factor = target_render_height / current_height
        
        new_w = int(img.width * scaling_factor)
        new_h = int(img.height * scaling_factor)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        new_alpha = img.split()[3]
        new_bbox = new_alpha.getbbox()
        
        # 1. Create a vertical gradient mask and multiply with alpha
        gradient = Image.new('L', (new_w, new_h), 255)
        grad_draw = ImageDraw.Draw(gradient)
        # Start fade earlier to allow BG lines to show through (PSD: Pass Through feel)
        fade_top = int(new_h * 0.40) 
        fade_bottom = new_h
        for y in range(fade_top, fade_bottom):
            # Soft linear fade towards the bottom
            alpha_val = int(255 * (1 - (y - fade_top) / (fade_bottom - fade_top)))
            grad_draw.line([(0, y), (new_w, y)], fill=alpha_val)
        
        # Combine existing player alpha with the gradient using ImageChops
        final_alpha = ImageChops.multiply(new_alpha, gradient)
        img.putalpha(final_alpha)
        
        # Restoring previous soft player halo (Lower intensity)
        self.draw_mask_glow(canvas, img, (center_x, target_y + (new_h/2) - (new_bbox[1])), 
                            color=(6, 191, 80, 200), dilation=6 * scale, blur=18 * scale, intensity=1.4)
        
        render_x = center_x - (new_w // 2)
        render_y = target_y - new_bbox[1]
        canvas.alpha_composite(img, (int(render_x), int(render_y)))

    def draw_mask_glow(self, canvas, img, center, color, dilation=15, blur=30, intensity=2.0):
        """Logonun/Oyuncunun çevresini saran neon hale efekti."""
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        # Daha keskin ve parlak bir hale için margin ve blur kontrolü
        margin = blur + 20
        glow_canvas = Image.new("RGBA", (img.width + margin*2, img.height + margin*2), (0,0,0,0))
        alpha = img.split()[3]
        
        def force_odd(n):
            n = max(1, int(n))
            return n if n % 2 != 0 else n + 1
            
        # Core Glow (Saturated)
        ambient_mask = alpha.filter(ImageFilter.MaxFilter(force_odd(dilation)))
        outer_glow = Image.merge("RGBA", (
            Image.new("L", img.size, color[0]), Image.new("L", img.size, color[1]), Image.new("L", img.size, color[2]),
            ambient_mask
        ))
        glow_canvas.paste(outer_glow, (margin, margin), outer_glow)
        
        # Apply intense blur
        glow_canvas = glow_canvas.filter(ImageFilter.GaussianBlur(blur))
        
        # Opaklık Artırma: Core kısımları daha parlak yap
        r, g, b, a = glow_canvas.split()
        # Dynamic intensity boost
        a = a.point(lambda i: min(255, int(i * (intensity * (color[3]/255.0))))) 
        glow_canvas = Image.merge("RGBA", (r, g, b, a))
        
        # Composite under the object
        canvas.alpha_composite(glow_canvas, (int(center[0] - glow_canvas.width//2), int(center[1] - glow_canvas.height//2)))

    def draw_glow(self, canvas, pos, radius, color):
        """Legacy radial glow for background depth."""
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        left, top = pos[0] - radius, pos[1] - radius
        right, bottom = pos[0] + radius, pos[1] + radius
        draw.ellipse([left, top, right, bottom], fill=color)
        blurred = overlay.filter(ImageFilter.GaussianBlur(radius // 2))
        canvas.alpha_composite(blurred)
