import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat120(ZiraatBase):
    def render(self, data):
        """Standard Ziraat 120x600 (Ground Truth Version)."""
        width, height = 120, 600
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(canvas)
        
        # 1. Background (Vertical crop)
        bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_120x600_clean.png"
        if os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
            canvas.paste(bg, (0, 0))
        else:
            canvas.paste((240, 240, 240, 255), [0, 0, width, height])

        # Ziraat Vertical Logo for vertical banner
        z_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "ziraat_logo.png")

        if os.path.exists(z_logo_path):
            z_img = Image.open(z_logo_path).convert("RGBA")
            # Proportional scale to fit roughly 100px width
            z_img.thumbnail((100, 100), Image.Resampling.LANCZOS)
            canvas.alpha_composite(z_img, ((width - z_img.width)//2, 28))

        # 3. Side-by-Side Players (X=2 and X=61, Y=163)
        # Left: (2, 163, 57, 77), Logo Overlay: (13, 229, 36, 42)
        # Right: (61, 163, 57, 77), Logo Overlay: (69, 229, 43, 43)
        self.draw_player_block_vertical(canvas, data, 1, (2, 163, 57, 77), (13, 229, 36, 42))
        self.draw_player_block_vertical(canvas, data, 2, (61, 163, 57, 77), (69, 229, 43, 43))

        # 4. Vertical Match Info Stack (Starting at Y=309)
        self.draw_match_typography_vertical(canvas, data, (6, 309, 109, 100))

        # 5. Hemen Oyna Button (19, 460, 83, 25)
        ho_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/hemen_oyna_320x100.png"
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((83, 25), Image.Resampling.LANCZOS)
            canvas.alpha_composite(ho_img, (19, 460))

        # 6. Nesine Bottom Area (Box: -5, 542, 133, 70, Logo: 22, 549, 78, 38)
        self.draw_nesine_area_vertical(canvas, (-5, 542, 133, 70), (22, 549, 78, 38))

        # Save Output
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_120x600.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        canvas.save(out_path)
        return out_path

    def draw_player_block_vertical(self, canvas, data, index, bounds, logo_bounds):
        lx, ly, lw, lh = bounds
        t_colors = self.get_team_colors(data.get(f"team_{index}"))
        p_path = data.get(f"player_{index}_path")
        
        draw = ImageDraw.Draw(canvas)
        # Yellow Frame
        draw.rectangle([lx, ly, lx+lw, ly+lh], outline=(252, 215, 0, 255), width=1)
        
        # Pill Inner (Smaller radii for narrow view)
        mask_size = (lw-4, lh-4)
        pill_mask = self.create_player_mask(mask_size, radii=(max(15, mask_size[0]//2), 5, 5, 5))
        pill_bg = Image.new("RGBA", mask_size, t_colors["p"])
        
        pill_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
        pill_final.paste(pill_bg, (0, 0), pill_mask)
        canvas.alpha_composite(pill_final, (lx+2, ly+2))
        
        if p_path and os.path.exists(p_path):
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), mask_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
            p_final.paste(p_img, (0, 0), pill_mask)
            canvas.alpha_composite(p_final, (lx+2, ly+2))

        # Logo Overlap
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            l_img.thumbnail((logo_bounds[2], logo_bounds[3]), Image.Resampling.LANCZOS)
            clx = logo_bounds[0] + (logo_bounds[2] - l_img.width)//2
            cly = logo_bounds[1] + (logo_bounds[3] - l_img.height)//2
            canvas.alpha_composite(l_img, (clx, cly))

    def draw_match_typography_vertical(self, canvas, data, bounds):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        try:
            t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
            hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
            
            # Helper for auto-scaling font
            def get_scaling_font(text, base_size, max_w):
                s = base_size
                f = ImageFont.truetype(self.font_bold, s)
                while draw.textlength(text, font=f) > max_w and s > 12:
                    s -= 1
                    f = ImageFont.truetype(self.font_bold, s)
                return f

            f1 = get_scaling_font(t1, 20, bw)
            f2 = get_scaling_font(t2, 20, bw)
            font_info = ImageFont.truetype(self.font_reg, 16)
            
            # Team 1
            tw1 = draw.textlength(t1, font=f1)
            draw.text((bx + (bw - tw1)//2, by), t1, font=f1, fill="black")
            # Team 2
            tw2 = draw.textlength(t2, font=f2)
            draw.text((bx + (bw - tw2)//2, by + 30), t2, font=f2, fill="black")
            
            # Info (Y=372 from plan)
            iy = 372
            tw_h = draw.textlength(hour, font=font_info)
            draw.text((bx + (bw - tw_h)//2, iy), hour, font=font_info, fill="black")
            tw_d = draw.textlength(day, font=font_info)
            draw.text((bx + (bw - tw_d)//2, iy + 20), day, font=font_info, fill="black")
        except: pass

    def draw_nesine_area_vertical(self, canvas, box_bounds, logo_bounds):
        bx, by, bw, bh = box_bounds
        lx, ly, lw, lh = logo_bounds
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(252, 215, 0, 255))
        
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((lw, lh), Image.Resampling.LANCZOS)
            canvas.alpha_composite(n_img, (lx + (lw - n_img.width)//2, ly + (lh - n_img.height)//2))
