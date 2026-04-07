import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from .ziraat_base import ZiraatBase

class Ziraat1200(ZiraatBase):
    def render(self, data):
        """Standard Ziraat 1200x628 (Ground Truth Version)."""
        width, height = 1200, 628
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(canvas)
        
        # 1. Background
        bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_ultra_clean.png"
        if os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
            canvas.paste(bg, (0, 0))
        else:
            canvas.paste((240, 240, 240, 255), [0, 0, width, height])

        # 2. Top Ziraat Logo Vertical (Center Top)
        z_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "ziraat_logo.png")
        if os.path.exists(z_logo_path):
            z_img = Image.open(z_logo_path).convert("RGBA")
            # Apply AI Overrides for logo scale if present
            z_scale = self.overrides.get("ziraat_logo_scale", 1.0)
            z_img.thumbnail((int(150 * z_scale), int(150 * z_scale)), Image.Resampling.LANCZOS)
            
            # Center the logo, with Y override
            lx = (width - z_img.width)//2
            ly = self.overrides.get("ziraat_logo_y", 26)
            canvas.alpha_composite(z_img, (lx, ly))

        # 3. Player Blocks
        # Left: (28, 55, 303, 375), Logo: (137, 367, 100, 119)
        p1_y = self.overrides.get("player_1_y", 55)
        p2_y = self.overrides.get("player_2_y", 56)
        self.draw_player_block(canvas, data, 1, (28, p1_y, 303, 375), (137, 367, 100, 119))
        self.draw_player_block(canvas, data, 2, (870, p2_y, 303, 372), (956, 367, 118, 118))

        # 4. Team Names (364, 196, 472, 113) - PSD Ground Truth
        self.draw_match_typography(canvas, data, (364, 196, 472, 113))

        # 5. Match Info Boxes (506, 344, 189, 71)
        self.draw_match_info_boxes(canvas, data, (506, 344, 189, 71))

        # 6. Hemen Oyna Button (501, 439, 200, 63)
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "hemen_oyna.png")
        if not os.path.exists(ho_path):
             ho_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/hemen_oyna_320x100.png"
        
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((200, 63), Image.Resampling.LANCZOS)
            ho_y = self.overrides.get("hemen_oyna_y", 439)
            canvas.alpha_composite(ho_img, (501, ho_y))

        # 7. Nesine Bottom Area (480, 526, 240, 103)
        self.draw_nesine_area(canvas, (480, 526, 240, 103))

        # Save Output
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_1200x628.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        canvas.save(out_path)
        return out_path

    def draw_player_block(self, canvas, data, index, bounds, logo_bounds):
        lx, ly, lw, lh = bounds
        t_colors = self.get_team_colors(data.get(f"team_{index}"))
        p_path = data.get(f"player_{index}_path")
        
        # A. Classic Pill Backdrop (Bunu ilerde dinamik yapacağız - Şimdilik klasik)
        # self.draw_dynamic_backdrop(canvas, (lx+5, ly+5, mask_size[0], mask_size[1]), t_colors["p"], t_colors["s"], 1)
        
        # Simple Shape Background (Match original silhouette)
        mask_size = (lw, lh) # Fill the entire block width/height
        # Only top-left corner is rounded in original
        pill_mask = self.create_player_mask(mask_size, radii=(int(mask_size[0] * 0.45), 0, 0, 0))
        pill_bg = Image.new("RGBA", mask_size, t_colors["p"])
        
        # Aura waves (Legacy static waves)
        waves_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates/backdrop_waves_v3.png"
        if os.path.exists(waves_path):
            waves = Image.open(waves_path).convert("RGBA").resize(mask_size, Image.Resampling.LANCZOS)
            pill_bg = Image.alpha_composite(pill_bg, waves)
            
        pill_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
        pill_final.paste(pill_bg, (0, 0), pill_mask)
        canvas.alpha_composite(pill_final, (lx, ly))
        
        # B. Black Outer Frame (Matches original)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([lx, ly, lx+lw, ly+lh], outline="black", width=3)
        
        # C. Player Image (Enlarged head / Scaled up with Overrides)
        if p_path and os.path.exists(p_path):
            p_img_orig = Image.open(p_path).convert("RGBA")
            
            # Dynamic Scale and Offsets
            p_scale = float(self.overrides.get(f"player_{index}_scale", 1.5))
            px_off = int(self.overrides.get(f"player_{index}_x_offset", 0))
            py_off = int(self.overrides.get(f"player_{index}_y_offset", 0))
            
            new_w = int(mask_size[0] * p_scale)
            new_h = int(p_img_orig.height * (new_w / p_img_orig.width))
            p_img_scaled = p_img_orig.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Crop to mask_size, with offsets
            left = (new_w - mask_size[0]) // 2 - px_off
            top = -py_off # Positive shifts up by convention or crop
            
            # Bounds check
            left = max(0, min(left, new_w - mask_size[0]))
            top = max(0, min(top, new_h - mask_size[1]))
            
            p_img_cropped = p_img_scaled.crop((left, top, left + mask_size[0], top + mask_size[1]))
            
            p_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
            p_final.paste(p_img_cropped, (0, 0), pill_mask)
            canvas.alpha_composite(p_final, (lx+5, ly+5))

        # D. Team Logo Overlap
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            
            # Logo Scaling
            l_scale = float(self.overrides.get(f"logo_{index}_scale", 1.0))
            target_w = int(logo_bounds[2] * l_scale)
            target_h = int(logo_bounds[3] * l_scale)
            l_img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Logo Offsets
            lx_off = int(self.overrides.get(f"logo_{index}_x_offset", 0))
            ly_off = int(self.overrides.get("logo_y_offset", 0))
            
            # Center the logo within its box, then apply offsets
            clx = logo_bounds[0] + (logo_bounds[2] - l_img.width)//2 + lx_off
            cly = logo_bounds[1] + (logo_bounds[3] - l_img.height)//2 + ly_off
            canvas.alpha_composite(l_img, (clx, cly))

    def draw_match_typography(self, canvas, data, bounds):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        try:
            t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
            
            # Team Names: FS and Y Offsets
            orig_fs = 72
            fs = self.overrides.get("team_name_fs", orig_fs)
            font_team = ImageFont.truetype(self.font_bold, fs)
            
            # Dynamic Y-positioning
            # ty uses by as anchor, with optional match_title_y_offset / team_name_y_offset
            ty = self.overrides.get("team_name_y", by + 190) + int(self.overrides.get("team_name_y_offset", 0))

            # Shrink-to-fit logic
            while (draw.textlength(t1, font=font_team) > bw or draw.textlength(t2, font=font_team) > bw) and fs > 40:
                fs -= 2
                font_team = ImageFont.truetype(self.font_bold, fs)
            
            # Draw with spacing / center logic
            self.draw_text_with_spacing(draw, t1, (bx, ty), font_team, fill="black", target_width=bw)
            self.draw_text_with_spacing(draw, t2, (bx, ty + fs + 5), font_team, fill="black", target_width=bw)
            
            # --- MAIN MATCH TITLE (headline) ---
            title = data.get("match_title", "MAÇ BAŞLIYOR").upper()
            mt_fs = self.overrides.get("match_title_fs", 28)
            mt_y_off = int(self.overrides.get("match_title_y_offset", 0))
            mt_x_off = int(self.overrides.get("match_title_x_offset", 0))
            font_title = ImageFont.truetype(self.font_reg, mt_fs)
            tw_title = draw.textlength(title, font=font_title)
            # Standard PSD position (y=40 relative to bounds)
            draw.text((bx + (bw - tw_title)//2 + mt_x_off, by + 40 + mt_y_off), title, font=font_title, fill=(30, 30, 30, 255))
            
        except Exception as e:
            print(f"Typography Error: {e}")

    def draw_match_info_boxes(self, canvas, data, bounds):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        try:
            # Match Info: FS and Position Dynamic Control
            fs_info = self.overrides.get("match_info_fs", 40)
            font_info = ImageFont.truetype(self.font_reg, fs_info)
            hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
            
            # Positional Control
            info_y = self.overrides.get("match_info_y", by) + int(self.overrides.get("match_info_y_offset", 0))
            info_x_off = int(self.overrides.get("match_info_x_offset", 0))
            
            tw1 = draw.textlength(hour, font=font_info)
            draw.text((bx + (bw - tw1)//2 + info_x_off, info_y), hour, font=font_info, fill="black")
            
            tw2 = draw.textlength(day, font=font_info)
            draw.text((bx + (bw - tw2)//2 + info_x_off, info_y + fs_info + 5), day, font=font_info, fill="black")
        except Exception as e:
            print(f"Info Box Error: {e}")

    def draw_nesine_area(self, canvas, bounds):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        # Updated to #fbc600 and exact PSD (480, 526, 240, 103)
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(251, 198, 0, 255))
        
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            # Exact PSD size (157, 76)
            n_img = n_img.resize((157, 76), Image.Resampling.LANCZOS)
            # Apply sharpening to prevent blur in smaller formats / compression
            from PIL import ImageFilter
            n_img = n_img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
            
            # Exact PSD position (522, 539)
            canvas.alpha_composite(n_img, (522, 539))
