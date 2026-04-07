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

        # Asset Paths
        z_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "ziraat_logo.png")
        ho_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/hemen_oyna_320x100.png"

        # 3. Side-by-Side Players (Stay at 2x)
        p1_y = self.overrides.get("player_1_y", 163) * scale
        p2_y = self.overrides.get("player_2_y", 163) * scale
        self.draw_player_block_vertical(canvas, data, 1, (2 * scale, p1_y, 57 * scale, 77 * scale), (13 * scale, p1_y + 66 * scale, 36 * scale, 42 * scale), scale)
        self.draw_player_block_vertical(canvas, data, 2, (61 * scale, p2_y, 57 * scale, 77 * scale), (69 * scale, p2_y + 66 * scale, 43 * scale, 43 * scale), scale)

        # 4. Vertical Match Info Stack (Stay at 2x for smooth typography)
        match_y = self.overrides.get("match_info_y", 309) * scale
        self.draw_match_typography_vertical(canvas, data, (6 * scale, match_y, 109 * scale, 100 * scale), scale)

        # 5. Post-Processing: Downsample First
        final_canvas = canvas.resize((sw, sh), Image.Resampling.LANCZOS)
        from PIL import ImageFilter
        final_canvas = final_canvas.filter(ImageFilter.UnsharpMask(radius=1.0, percent=50, threshold=3))
        
        # 6. POST-DOWNSAMPLE BRANDING (1x scale for maximum sharpness)
        # These are now only resized ONCE to their final display size
        
        # A. Ziraat Logo (41, 28, 41, 54 at 1x)
        if os.path.exists(z_logo_path):
            z_img = Image.open(z_logo_path).convert("RGBA")
            z_img = z_img.resize((41, 54), Image.Resampling.LANCZOS)
            z_y = self.overrides.get("ziraat_logo_y", 28)
            final_canvas.alpha_composite(z_img, (41, z_y))

        # B. Hemen Oyna Button (19, 460, 83, 25 at 1x)
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((83, 25), Image.Resampling.LANCZOS)
            ho_y = self.overrides.get("hemen_oyna_y", 460)
            final_canvas.alpha_composite(ho_img, (19, ho_y))

        # C. Nesine Bottom Area (Bounds are now 1x: -5, 542, 133, 70)
        self.draw_nesine_area_vertical(final_canvas, (-5, 542, 133, 70), (22, 549, 78, 38), 1)

        # 7. Save Output
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
            p_scale = self.overrides.get(f"player_{index}_scale", self.overrides.get("player_scale", 1.0))
            target_size = (int(mask_size[0] * p_scale), int(mask_size[1] * p_scale))
            
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), target_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_mask = self.create_player_mask(target_size, radii=(max(15 * scale, target_size[0]//2), 5 * scale, 5 * scale, 5 * scale))
            p_bg = Image.new("RGBA", target_size, t_colors["p"])
            
            p_final = Image.new("RGBA", target_size, (0, 0, 0, 0))
            p_final.paste(p_bg, (0, 0), p_mask)
            p_final.paste(p_img, (0, 0), p_mask)
            
            px_final = int(lx+2 * scale - (target_size[0]-mask_size[0])//2) + int(self.overrides.get(f"player_{index}_x_offset", 0)) * scale
            py_final = int(ly+2 * scale - (target_size[1]-mask_size[1])//2) + int(self.overrides.get(f"player_{index}_y_offset", 0)) * scale
            canvas.alpha_composite(p_final, (px_final, py_final))

        # Logo Control: Scale and Offset
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            
            l_scale = float(self.overrides.get(f"logo_{index}_scale", 1.0))
            lw_final, lh_final = int(logo_bounds[2] * l_scale), int(logo_bounds[3] * l_scale)
            l_img.thumbnail((lw_final, lh_final), Image.Resampling.LANCZOS)
            
            lx_off = int(self.overrides.get(f"logo_{index}_x_offset", 0)) * scale
            ly_off = int(self.overrides.get("logo_y_offset", 0)) * scale
            
            clx = logo_bounds[0] + (logo_bounds[2] - l_img.width)//2 + lx_off
            cly = logo_bounds[1] + (logo_bounds[3] - l_img.height)//2 + ly_off
            canvas.alpha_composite(l_img, (clx, cly))

    def draw_match_typography_vertical(self, canvas, data, bounds, scale):
        bx, by, bw, bh = bounds
        draw = ImageDraw.Draw(canvas)
        try:
            t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
            hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
            
            f_reg = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat/MonumentExtended-Regular.otf"
            f_bold = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat/MonumentExtended-Ultrabold.otf"

            # Helper for auto-scaling team names
            def get_scaling_font(text, base_size, max_w, font_path):
                s = base_size
                f = ImageFont.truetype(font_path, int(s * scale))
                while draw.textlength(text, font=f) > max_w and s > 12:
                    s -= 1
                    f = ImageFont.truetype(font_path, int(s * scale))
                return f

            f_team1 = get_scaling_font(t1, 16, bw, f_bold)
            f_team2 = get_scaling_font(t2, 16, bw, f_bold)
            
            # 1. Hour (Master Width)
            # PSD says 24px
            f_hour = ImageFont.truetype(f_reg, 24 * scale)
            hw = draw.textlength(hour, font=f_hour)
            
            # 2. Day (Match width of hour)
            # Find best font size starting from 11.5px
            ds = 11.5
            f_day = ImageFont.truetype(f_reg, int(ds * scale))
            cur_w = draw.textlength(day, font=f_day)
            
            # Binary-like search or iterative adjustment
            if cur_w > hw:
                while draw.textlength(day, font=f_day) > hw and ds > 4:
                    ds -= 0.5
                    f_day = ImageFont.truetype(f_reg, int(ds * scale))
            else:
                while draw.textlength(day, font=f_day) < hw and ds < 24:
                    ds += 0.5
                    f_day = ImageFont.truetype(f_reg, int(ds * scale))
            
            # Team Positioning with Offsets
            t1_x_off = int(self.overrides.get("team_1_x_offset", 0)) * scale
            t2_x_off = int(self.overrides.get("team_2_x_offset", 0)) * scale
            t_y_off = int(self.overrides.get("team_name_y_offset", 0)) * scale
            
            tw1 = draw.textlength(t1, font=f_team1)
            draw.text((bx + (bw - tw1)//2 + t1_x_off, by + t_y_off), t1, font=f_team1, fill="black")
            # Team 2
            tw2 = draw.textlength(t2, font=f_team2)
            draw.text((bx + (bw - tw2)//2 + t2_x_off, by + 24 * scale + t_y_off), t2, font=f_team2, fill="black")
            
            # Date Area: FS and Position Control
            info_fs = self.overrides.get("match_info_fs", 24)
            f_hour = ImageFont.truetype(f_reg, int(info_fs * scale))
            hw = draw.textlength(hour, font=f_hour)
            
            iy = (372 + self.overrides.get("match_info_y_offset", 0)) * scale
            ix_off = int(self.overrides.get("match_info_x_offset", 0)) * scale
            
            # Draw Hour
            draw.text((bx + (bw - hw)//2 + ix_off, iy), hour, font=f_hour, fill="black")
            # Draw Day
            dw = draw.textlength(day, font=f_day)
            draw.text((bx + (bw - dw)//2 + ix_off, iy + 25 * scale), day, font=f_day, fill="black")
        except Exception as e:
            print(f"Vertical Typography Error: {e}")

    def draw_nesine_area_vertical(self, canvas, box_bounds, logo_bounds, scale):
        bx, by, bw, bh = box_bounds
        lx, ly, lw, lh = logo_bounds
        draw = ImageDraw.Draw(canvas)
        # Updated to #fbc600 to match the master layout
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(251, 198, 0, 255))
        
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((lw, lh), Image.Resampling.LANCZOS)
            canvas.alpha_composite(n_img, (lx + (lw - n_img.width)//2, ly + (lh - n_img.height)//2))
