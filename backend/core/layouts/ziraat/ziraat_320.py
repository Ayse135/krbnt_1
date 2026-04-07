import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat320(ZiraatBase):
    def render(self, data):
        """Refined Ziraat 320x100 GIF with Supersampling (2x)."""
        sw, sh = 320, 100
        scale = 2
        width, height = sw * scale, sh * scale
        rgb_frames = []
        scenes = ["320x100_1.json", "320x100_2.json", "320x100_3.json"]
        
        # Post-Processing: Downsample & Sharpen + Layer Branding at 1x
        def post_process(img, scene_id):
            # 1. Resize layout to final 1x
            img = img.resize((sw, sh), Image.Resampling.LANCZOS)
            from PIL import ImageFilter
            img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=50, threshold=3))
            
            # 2. Add Branding at 1x scale for maximum sharpness
            if scene_id == 1:
                # Ziraat Logo (84, 8, 150, 58)
                # Ziraat logo in 320x100 is ztk_yatay_logo.png
                z_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
                if os.path.exists(z_path):
                    z_img = Image.open(z_path).convert("RGBA").resize((150, 58), Image.Resampling.LANCZOS)
                    z_y = self.overrides.get("ziraat_logo_y", 8)
                    img.alpha_composite(z_img, (84, z_y))
                # Nesine Area (129, 68, 60, 42)
                self.draw_nesine_area_gt(img, (129, 68, 60, 42), (137, 72, 45, 23), 1)

            elif scene_id == 2:
                # Nesine (129, 68, 60, 42) - STACKED BOTTOM
                self.draw_nesine_area_gt(img, (129, 68, 60, 42), (137, 72, 45, 23), 1)
                # Hemen Oyna (129, 43, 62, 20) - STACKED TOP
                self.draw_hemen_oyna_badge(img, (129, 43, 62, 20), 1)

            elif scene_id == 3:
                # Nesine centered (X=130) and Hemen Oyna to its right
                # Nesine Area (130, 68, 60, 42)
                self.draw_nesine_area_gt(img, (130, 68, 60, 42), (138, 72, 45, 23), 1)
                # Hemen Oyna (195, 70, 62, 20)
                self.draw_hemen_oyna_badge(img, (195, 70, 62, 20), 1)
                
            return img.convert("RGB")

        for scene_idx, scene_file in enumerate(scenes):
            scene_id = scene_idx + 1
            frame = Image.new("RGBA", (width, height), (240, 240, 240, 255))
            
            # Global Background
            bg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bg_320x100_clean.png")
            if os.path.exists(bg_path):
                 bg = Image.open(bg_path).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
                 frame.paste(bg, (0, 0))

            if scene_id == 1:
                self.draw_scene_1(frame, data, scale)
            elif scene_id == 2:
                self.draw_scene_2(frame, data, scale)
            elif scene_id == 3:
                self.draw_scene_3(frame, data, scale)
            
            rgb_frames.append(post_process(frame, scene_id))

        # GIF Generation
        output_path = self.save_gif_optimized(rgb_frames, "banner_320x100.gif", durations=[2000, 3500, 4000])
        return output_path

    def draw_scene_1(self, frame, data, scale):
        """Scene 1: Layout only (Branding moved to post_process)."""
        pass

    def draw_scene_2(self, frame, data, scale):
        """Scene 2: Players with Logos beside them (Ground Truth)."""
        # Exact PSD coordinates from 2.psd/3.psd
        # Left Side
        self.draw_player_with_logo(frame, data, 1, (9 * scale, 5 * scale, 64 * scale, 85 * scale), (70 * scale, 24 * scale, 43 * scale, 59 * scale), scale)
        # Right Side
        self.draw_player_with_logo(frame, data, 2, (243 * scale, 6 * scale, 64 * scale, 84 * scale), (199 * scale, 24 * scale, 57 * scale, 59 * scale), scale)

    def draw_scene_3(self, frame, data, scale):
        """Scene 3: Refined 2x2 Grid (Branding moved to post_process)."""
        draw = ImageDraw.Draw(frame)
        t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
        hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
        
        f_reg = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat/MonumentExtended-Regular.otf"
        f_bold = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat/MonumentExtended-Ultrabold.otf"
        
        # Dynamic Scaling Helper for teams
        def get_font_scaled(text, base_size, max_w, font_path):
            s = self.overrides.get("team_name_fs", base_size)
            f = ImageFont.truetype(font_path, int(s * scale))
            while draw.textlength(text, font=f) > max_w * scale and s > 12:
                s -= 1
                f = ImageFont.truetype(font_path, int(s * scale))
            return f

        # Column 1 (X=13): Teams (Stacked per screenshot)
        # PSD bounds: 13, 17, 170, 50. Width is 170.
        target_w = 170 * scale
        
        # Find font size that fits the longer team name into target_w
        fs = 26
        f_team = ImageFont.truetype(f_bold, int(fs * scale))
        while (draw.textlength(t1, font=f_team) > target_w or draw.textlength(t2, font=f_team) > target_w) and fs > 12:
            fs -= 1
            f_team = ImageFont.truetype(f_bold, int(fs * scale))
        
        # Draw both with exact same width (target_w) using letter spacing
        # Dynamic Positioning
        t_y_off = int(self.overrides.get("team_name_y_offset", 0)) * scale
        
        ty_1 = (self.overrides.get("team_1_y", 20) * scale) + t_y_off
        ty_2 = (self.overrides.get("team_2_y", 42) * scale) + t_y_off
        # If title_y is used, we need to shift the second team relative to it
        if "title_y" in self.overrides:
             ty_2 = ty_1 + (fs + 5) * scale

        t1_x_off = int(self.overrides.get("team_1_x_offset", 0)) * scale
        t2_x_off = int(self.overrides.get("team_2_x_offset", 0)) * scale
        
        self.draw_text_with_spacing(draw, t1, (13 * scale + t1_x_off, ty_1), f_team, fill="black", target_width=target_w)
        self.draw_text_with_spacing(draw, t2, (13 * scale + t2_x_off, ty_2), f_team, fill="black", target_width=target_w)
        
        # Position and Scale Control for Info
        info_fs = self.overrides.get("match_info_fs", 25)
        f_hour = ImageFont.truetype(f_reg, int(info_fs * scale))
        hw = draw.textlength(hour, font=f_hour)
        
        # Day auto-fit logic
        ds = 12.5
        f_day = ImageFont.truetype(f_reg, int(ds * scale))
        while draw.textlength(day, font=f_day) > hw and ds > 4:
            ds -= 0.5
            f_day = ImageFont.truetype(f_reg, int(ds * scale))

        tx = (220 + self.overrides.get("match_info_x_offset", 0)) * scale
        ty = (self.overrides.get("match_info_y", 25) + self.overrides.get("match_info_y_offset", 0)) * scale
        draw.text((tx, ty), hour, font=f_hour, fill="black")
        # Center Day under Hour width
        dw = draw.textlength(day, font=f_day)
        draw.text((tx + (hw - dw)//2, ty + 28 * scale), day, font=f_day, fill="black")

    def draw_player_with_logo(self, frame, data, index, p_bounds, l_bounds, scale):
        px, py, pw, ph = p_bounds
        lx, ly, lw, lh = l_bounds
        t_colors = self.get_team_colors(data.get(f"team_{index}"))
        p_path = data.get(f"player_{index}_path")
        
        # Yellow Frame
        draw = ImageDraw.Draw(frame)
        draw.rectangle([px, py, px+pw, py+ph], outline=(252, 215, 0, 255), width=2 * scale)
        
        if p_path and os.path.exists(p_path):
            # Pill Mask Logic
            ps_w, ps_h = int(pw-4 * scale), int(ph-4 * scale)
            p_scale = self.overrides.get(f"player_{index}_scale", self.overrides.get("player_scale", 1.0))
            target_size = (int(ps_w * p_scale), int(ps_h * p_scale))
            
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), target_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_mask = self.create_player_mask(target_size, radii=(max(30 * scale, ph//2), 10 * scale, 10 * scale, 10 * scale))
            p_bg = Image.new("RGBA", target_size, t_colors["p"])
            
            p_final = Image.new("RGBA", target_size, (0,0,0,0))
            p_final.paste(p_bg, (0,0), p_mask)
            p_final.paste(p_img, (0,0), p_mask)
            
            px_final = int(px+2 * scale - (target_size[0]-ps_w)//2) + int(self.overrides.get(f"player_{index}_x_offset", 0)) * scale
            py_final = (self.overrides.get("player_1_y" if index==1 else "player_2_y", py//scale) + self.overrides.get(f"player_{index}_y_offset", 0)) * scale
            frame.alpha_composite(p_final, (px_final, int(py_final)))

        # Logo Control: Scale and Offset
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            
            l_scale = float(self.overrides.get(f"logo_{index}_scale", 1.0))
            lw_final, lh_final = int(lw * l_scale), int(lh * l_scale)
            l_img.thumbnail((lw_final, lh_final), Image.Resampling.LANCZOS)
            
            lx_off = int(self.overrides.get(f"logo_{index}_x_offset", 0)) * scale
            ly_off = int(self.overrides.get("logo_y_offset", 0)) * scale
            
            clx = lx + (lw - l_img.width)//2 + lx_off
            cly = ly + (lh - l_img.height)//2 + ly_off
            frame.alpha_composite(l_img, (clx, cly))

    def draw_nesine_area_gt(self, frame, box_bounds, logo_bounds, scale):
        bx, by, bw, bh = box_bounds
        lx, ly, lw, lh = logo_bounds
        draw = ImageDraw.Draw(frame)
        # Updated to #f8ba17 as requested
        draw.rectangle([bx * scale, by * scale, (bx + bw) * scale, (by + bh) * scale], fill=(248, 186, 23, 255))
        
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img = n_img.resize((int(lw), int(lh)), Image.Resampling.LANCZOS)
            frame.alpha_composite(n_img, (int(lx), int(ly)))

    def draw_hemen_oyna_badge(self, frame, bounds, scale):
        hx, hy, hw, hh = bounds
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "hemen_oyna_320x100.png")
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((int(hw), int(hh)), Image.Resampling.LANCZOS)
            frame.alpha_composite(ho_img, (int(hx), int(hy)))

    def save_gif_optimized(self, frames, filename, durations):
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        combined = Image.new("RGB", (frames[0].width * len(frames), frames[0].height))
        for i, f in enumerate(frames): combined.paste(f, (i * frames[0].width, 0))
        palette = combined.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
        p_frames = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
        p_frames[0].save(out_path, save_all=True, append_images=p_frames[1:], duration=durations, loop=0, optimize=False, disposal=2)
        return out_path
