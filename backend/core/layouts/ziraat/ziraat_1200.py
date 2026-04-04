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
            z_img.thumbnail((150, 150), Image.Resampling.LANCZOS)
            # Center the logo
            lx, ly = (width - z_img.width)//2, 26
            canvas.alpha_composite(z_img, (lx, ly))

        # 3. Player Blocks (X=28 and X=870)
        # Left: (28, 25, 303, 409), Logo: 1.5x size
        self.draw_player_block(canvas, data, 1, (28, 25, 303, 409), (112, 337, 150, 178))
        self.draw_player_block(canvas, data, 2, (870, 26, 303, 406), (926, 337, 177, 177))

        # 4. Team Names (364, 196, 472, 113)
        self.draw_match_typography(canvas, data, (364, 196, 472, 113))

        # 5. Match Info Boxes (506, 344, 189, 71)
        self.draw_match_info_boxes(canvas, data, (506, 344, 189, 71))

        # 6. Hemen Oyna Button (501, 439, 200, 63)
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "hemen_oyna.png")
        if not os.path.exists(ho_path):
             ho_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/hemen_oyna_320x100.png"
        
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((200, 63), Image.Resampling.LANCZOS)
            canvas.alpha_composite(ho_img, (501, 439))

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
        
        # A. Thin Yellow Outline
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([lx, ly, lx+lw, ly+lh], outline=(252, 215, 0, 255), width=2)
        
        # B. Pill Inner Background
        mask_size = (lw-10, lh-10) # Slight offset for frame padding
        pill_mask = self.create_player_mask(mask_size, radii=(max(40, mask_size[0]//2), 20, 20, 20))
        pill_bg = Image.new("RGBA", mask_size, t_colors["p"])
        
        # Aura waves (v3 style from assets)
        waves_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates/backdrop_waves_v3.png"
        if os.path.exists(waves_path):
            waves = Image.open(waves_path).convert("RGBA").resize(mask_size, Image.Resampling.LANCZOS)
            pill_bg = Image.alpha_composite(pill_bg, waves)
            
        pill_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
        pill_final.paste(pill_bg, (0, 0), pill_mask)
        canvas.alpha_composite(pill_final, (lx+5, ly+5))
        
        # C. Player Masked (Pop-out kafa serbest)
        if p_path and os.path.exists(p_path):
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), mask_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
            p_final.paste(p_img, (0, 0), pill_mask)
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
            font_team = ImageFont.truetype(self.font_bold, 55)
            t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
            
            # Draw stacked horizontally centered in the block
            tw1 = draw.textlength(t1, font=font_team)
            tw2 = draw.textlength(t2, font=font_team)
            
            draw.text((bx + (bw - tw1)//2, by), t1, font=font_team, fill="black")
            draw.text((bx + (bw - tw2)//2, by + 55), t2, font=font_team, fill="black")
        except: pass

    def draw_match_info_boxes(self, canvas, data, bounds):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        try:
            font_info = ImageFont.truetype(self.font_reg, 32)
            hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
            
            # No more boxes - User requested removal (Kutuları kaldır)
            tw1 = draw.textlength(hour, font=font_info)
            draw.text((bx + (bw - tw1)//2, by), hour, font=font_info, fill="black")
            
            tw2 = draw.textlength(day, font=font_info)
            draw.text((bx + (bw - tw2)//2, by + 40), day, font=font_info, fill="black")
        except: pass

    def draw_nesine_area(self, canvas, bounds):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        # Yellow Box
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(252, 215, 0, 255))
        # High-res Logo
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((157, 76), Image.Resampling.LANCZOS)
            canvas.alpha_composite(n_img, (bx + (bw-n_img.width)//2, by + (bh-n_img.height)//2))
