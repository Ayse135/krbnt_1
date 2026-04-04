import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat120(ZiraatBase):
    def render(self, data):
        """Standard Ziraat 120x600 with Supersampling (2x)."""
        sw, sh = 120, 600
        scale = 2
        width, height = sw * scale, sh * scale
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
            z_img.thumbnail((100 * scale, 100 * scale), Image.Resampling.LANCZOS)
            canvas.alpha_composite(z_img, ((width - z_img.width)//2, 28 * scale))

        # 3. Side-by-Side Players
        self.draw_player_block_vertical(canvas, data, 1, (2 * scale, 163 * scale, 57 * scale, 77 * scale), (13 * scale, 229 * scale, 36 * scale, 42 * scale), scale)
        self.draw_player_block_vertical(canvas, data, 2, (61 * scale, 163 * scale, 57 * scale, 77 * scale), (69 * scale, 229 * scale, 43 * scale, 43 * scale), scale)

        # 4. Vertical Match Info Stack
        self.draw_match_typography_vertical(canvas, data, (6 * scale, 309 * scale, 109 * scale, 100 * scale), scale)

        # 5. Hemen Oyna Button (19, 460, 83, 25)
        ho_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/hemen_oyna_320x100.png"
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((83 * scale, 25 * scale), Image.Resampling.LANCZOS)
            canvas.alpha_composite(ho_img, (19 * scale, 460 * scale))

        # 6. Nesine Bottom Area
        self.draw_nesine_area_vertical(canvas, (-5 * scale, 542 * scale, 133 * scale, 70 * scale), (22 * scale, 549 * scale, 78 * scale, 38 * scale), scale)

        # 7. Post-Processing: Downsample & Sharpen
        final_canvas = canvas.resize((sw, sh), Image.Resampling.LANCZOS)
        from PIL import ImageFilter
        final_canvas = final_canvas.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))

        # 8. Save Output
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_120x600.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        final_canvas.save(out_path)
        return out_path

    def draw_player_block_vertical(self, canvas, data, index, bounds, logo_bounds, scale):
        lx, ly, lw, lh = bounds
        t_colors = self.get_team_colors(data.get(f"team_{index}"))
        p_path = data.get(f"player_{index}_path")
        
        draw = ImageDraw.Draw(canvas)
        # Yellow Frame
        draw.rectangle([lx, ly, lx+lw, ly+lh], outline=(252, 215, 0, 255), width=1 * scale)
        
        # Pill Inner (Smaller radii for narrow view)
        mask_size = (int(lw-4 * scale), int(lh-4 * scale))
        pill_mask = self.create_player_mask(mask_size, radii=(max(15 * scale, mask_size[0]//2), 5 * scale, 5 * scale, 5 * scale))
        pill_bg = Image.new("RGBA", mask_size, t_colors["p"])
        
        pill_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
        pill_final.paste(pill_bg, (0, 0), pill_mask)
        canvas.alpha_composite(pill_final, (int(lx+2 * scale), int(ly+2 * scale)))
        
        if p_path and os.path.exists(p_path):
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), mask_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_final = Image.new("RGBA", mask_size, (0, 0, 0, 0))
            p_final.paste(p_img, (0, 0), pill_mask)
            canvas.alpha_composite(p_final, (int(lx+2 * scale), int(ly+2 * scale)))

        # Logo Overlap
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            l_img.thumbnail((logo_bounds[2], logo_bounds[3]), Image.Resampling.LANCZOS)
            clx = logo_bounds[0] + (logo_bounds[2] - l_img.width)//2
            cly = logo_bounds[1] + (logo_bounds[3] - l_img.height)//2
            canvas.alpha_composite(l_img, (clx, cly))

    def draw_match_typography_vertical(self, canvas, data, bounds, scale):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        try:
            t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
            hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
            
            # Helper for auto-scaling font
            def get_scaling_font(text, base_size, max_w):
                s = base_size
                f = ImageFont.truetype(self.font_bold, int(s * scale))
                while draw.textlength(text, font=f) > max_w and s > 12:
                    s -= 1
                    f = ImageFont.truetype(self.font_bold, int(s * scale))
                return f

            f1 = get_scaling_font(t1, 20, bw)
            f2 = get_scaling_font(t2, 20, bw)
            
            # Saira Style info for consistency
            f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
            font_info = ImageFont.truetype(f_saira, 16 * scale)
            
            # Team 1
            tw1 = draw.textlength(t1, font=f1)
            draw.text((bx + (bw - tw1)//2, by), t1, font=f1, fill="black")
            # Team 2
            tw2 = draw.textlength(t2, font=f2)
            draw.text((bx + (bw - tw2)//2, by + 30 * scale), t2, font=f2, fill="black")
            
            # Info (Y=372 from plan)
            iy = 372 * scale
            tw_h = draw.textlength(hour, font=font_info)
            draw.text((bx + (bw - tw_h)//2, iy), hour, font=font_info, fill="black")
            tw_d = draw.textlength(day, font=font_info)
            draw.text((bx + (bw - tw_d)//2, iy + 20 * scale), day, font=font_info, fill="#06BF50")
        except: pass

    def draw_nesine_area_vertical(self, canvas, box_bounds, logo_bounds, scale):
        bx, by, bw, bh = box_bounds
        lx, ly, lw, lh = logo_bounds
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(252, 215, 0, 255))
        
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((lw, lh), Image.Resampling.LANCZOS)
            canvas.alpha_composite(n_img, (lx + (lw - n_img.width)//2, ly + (lh - n_img.height)//2))
