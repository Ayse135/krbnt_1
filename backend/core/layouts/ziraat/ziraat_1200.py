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
        
        # C. Player Image (Enlarged head / Scaled up)
        if p_path and os.path.exists(p_path):
            p_img_orig = Image.open(p_path).convert("RGBA")
            # Zoom logic: Resize so width is 1.5x of mask width to make head much larger (closer look)
            zoom = 1.5
            new_w = int(mask_size[0] * zoom)
            new_h = int(p_img_orig.height * (new_w / p_img_orig.width))
            p_img_scaled = p_img_orig.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Crop to mask_size, centering horizontally and shifting up slightly
            left = (new_w - mask_size[0]) // 2
            top = 0 # Head at top
            p_img_cropped = p_img_scaled.crop((left, top, left + mask_size[0], top + mask_size[1]))
            
            p_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
            p_final.paste(p_img_cropped, (0, 0), pill_mask)
            canvas.alpha_composite(p_final, (lx+5, ly+5))

        # D. Team Logo Overlap
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            l_img.thumbnail((logo_bounds[2], logo_bounds[3]), Image.Resampling.LANCZOS)
            # Center the logo within its box
            clx = logo_bounds[0] + (logo_bounds[2] - l_img.width)//2
            cly = logo_bounds[1] + (logo_bounds[3] - l_img.height)//2
            canvas.alpha_composite(l_img, (clx, cly))

    def draw_match_typography(self, canvas, data, bounds):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        try:
            t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
            
            # Start at 72px or override
            fs = self.overrides.get("team_name_fs", 72)
            font_team = ImageFont.truetype(self.font_bold, fs)
            
            # Shrink-to-fit logic: If either name is wider than bw, scale down fs
            while (draw.textlength(t1, font=font_team) > bw or draw.textlength(t2, font=font_team) > bw) and fs > 40:
                fs -= 2
                font_team = ImageFont.truetype(self.font_bold, fs)
            
            # Use title_y if provided, else use default 'by'
            ty = self.overrides.get("title_y", by)
            
            # Draw both with exact same width (bw)
            self.draw_text_with_spacing(draw, t1, (bx, ty), font_team, fill="black", target_width=bw)
            self.draw_text_with_spacing(draw, t2, (bx, ty + fs + 5), font_team, fill="black", target_width=bw)
            
        except: pass

    def draw_match_info_boxes(self, canvas, data, bounds):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        try:
            # Match Info using the same family but Regular
            fs_info = self.overrides.get("match_info_fs", 40)
            font_info = ImageFont.truetype(self.font_reg, fs_info)
            hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
            
            info_y = self.overrides.get("match_info_y", by)
            
            tw1 = draw.textlength(hour, font=font_info)
            draw.text((bx + (bw - tw1)//2, info_y), hour, font=font_info, fill="black")
            
            tw2 = draw.textlength(day, font=font_info)
            draw.text((bx + (bw - tw2)//2, info_y + fs_info + 5), day, font=font_info, fill="black")
        except: pass

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
