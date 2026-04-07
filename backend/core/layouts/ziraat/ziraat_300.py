import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat300(ZiraatBase):
    def render(self, data):
        """Refined Ziraat 300x50 GIF with Supersampling (2x)."""
        sw, sh = 300, 50
        scale = 2
        width, height = sw * scale, sh * scale
        rgb_frames = []
        
        # Post-Processing: Downsample & Sharpen + Layer Branding at 1x
        def post_process(img, scene_id):
            # 1. Resize layout to final 1x
            img = img.resize((sw, sh), Image.Resampling.LANCZOS)
            from PIL import ImageFilter
            img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=50, threshold=3))
            
            # 2. Add Branding at 1x scale for maximum sharpness
            # Nesine Area (0, 0, 66, 50) and Hemen Oyna (233, 16, 60, 19)
            self.draw_nesine_area_tiny(img, (0, 0, 66, 50), (233, 16, 60, 19), 1)

            if scene_id == 1:
                # Ziraat Logo (122x47 at [88, 1])
                z_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
                if os.path.exists(z_path):
                    z_img = Image.open(z_path).convert("RGBA").resize((122, 47), Image.Resampling.LANCZOS)
                    z_y = self.overrides.get("ziraat_logo_y", 1)
                    img.alpha_composite(z_img, (88, z_y))
                
            return img.convert("RGB")

        # Scenes Logic
        for scene_id in [1, 2, 3]:
            frame = Image.new("RGBA", (width, height), (240, 240, 240, 255))
            
            # Global Background (Short)
            bg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bg_300x50_clean.png")
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

        # Save GIF
        output_path = self.save_gif_standard(rgb_frames, "banner_300x50.gif", durations=[2000, 3500, 4000])
        return output_path

    def draw_scene_1(self, frame, data, scale):
        """Layout only (Branding moved to post_process)."""
        pass

    def draw_scene_2(self, frame, data, scale):
        """Micro Side-by-side Players and Logos (Ground Truth)."""
        # Exact PSD coordinates from 2.psd
        # Left Side (Player 1 then Logo 1)
        self.draw_player_micro(frame, data, 1, (81 * scale, 2 * scale, 35 * scale, 46 * scale), (112 * scale, 10 * scale, 33 * scale, 36 * scale), scale)
        # Right Side (Logo 2 then Player 2) - Logo 2 enlarged to 33px to match Logo 1
        self.draw_player_micro(frame, data, 2, (181 * scale, 2 * scale, 35 * scale, 46 * scale), (161 * scale, 10 * scale, 33 * scale, 36 * scale), scale)

    def draw_scene_3(self, frame, data, scale):
        """Match Info Grid shifted for Left Branding."""
        draw = ImageDraw.Draw(frame)
        t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
        hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()

        f_reg = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat/MonumentExtended-Regular.otf"
        f_bold = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/ziraat/MonumentExtended-Ultrabold.otf"
        
        # Helper: Find font size to fit width
        def get_font_fit(text, base_size, max_w, font_path):
            s = base_size
            f = ImageFont.truetype(font_path, int(s * scale))
            while draw.textlength(text, font=f) > max_w * scale and s > 8:
                s -= 1
                f = ImageFont.truetype(font_path, int(s * scale))
            return f

        # Column 1 (X=70): Teams
        target_w = 95 * scale
        fs = self.overrides.get("team_name_fs", 11)
        f_team = ImageFont.truetype(f_bold, int(fs * scale))
        while (draw.textlength(t1, font=f_team) > target_w or draw.textlength(t2, font=f_team) > target_w) and fs > 8:
            fs -= 1
            f_team = ImageFont.truetype(f_bold, int(fs * scale))
        
        # Team Position Control (with scale)
        t_y_off = int(self.overrides.get("team_name_y_offset", 0)) * scale
        ty_teams = (self.overrides.get("team_name_y", 13) * scale) + t_y_off
        t_x_off = int(self.overrides.get("team_name_x_offset", 0)) * scale
        
        # Draw both with exact same width (target_w) using letter spacing
        self.draw_text_with_spacing(draw, t1, (70 * scale + t_x_off, ty_teams), f_team, fill="black", target_width=target_w)
        self.draw_text_with_spacing(draw, t2, (70 * scale + t_x_off, ty_teams + 13 * scale), f_team, fill="black", target_width=target_w)
        
        # Column 2: Match Info (Time block)
        info_fs = self.overrides.get("match_info_fs", 15)
        f_hour = ImageFont.truetype(f_reg, int(info_fs * scale))
        hw = draw.textlength(hour, font=f_hour)
        
        # Day auto-fit
        ds = 8
        f_day = ImageFont.truetype(f_reg, int(ds * scale))
        while draw.textlength(day, font=f_day) > hw and ds > 4:
            ds -= 0.5
            f_day = ImageFont.truetype(f_reg, int(ds * scale))
        
        tx = (175 + self.overrides.get("match_info_x_offset", 0)) * scale
        ty = (self.overrides.get("match_info_y", 13) + self.overrides.get("match_info_y_offset", 0)) * scale
        draw.text((tx, ty), hour, font=f_hour, fill="black")
        # Center Day under Hour
        dw = draw.textlength(day, font=f_day)
        draw.text((tx + (hw - dw)//2, ty + 16 * scale), day, font=f_day, fill="black")
        dw = draw.textlength(day, font=f_day)
        draw.text((tx + (hw - dw)//2, ty + 16 * scale), day, font=f_day, fill="black")

    def draw_player_micro(self, frame, data, index, bounds, logo_bounds, scale):
        px, py, pw, ph = bounds
        lx, ly, lw, lh = logo_bounds
        t_colors = self.get_team_colors(data.get(f"team_{index}"))
        p_path = data.get(f"player_{index}_path")
        
        draw = ImageDraw.Draw(frame)
        # Micro frame
        draw.rectangle([px, py, px+pw, py+ph], outline=(252, 215, 0, 255), width=1 * scale)
        
        if p_path and os.path.exists(p_path):
            ps_w, ps_h = int(pw-2 * scale), int(ph-2 * scale)
            # Support individual scaling from AI
            p_scale = self.overrides.get(f"player_{index}_scale", self.overrides.get("player_scale", 1.0))
            target_size = (int(ps_w * p_scale), int(ps_h * p_scale))
            
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), target_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_mask = self.create_player_mask(target_size, radii=(10 * scale, 5 * scale, 5 * scale, 5 * scale))
            p_bg = Image.new("RGBA", target_size, t_colors["p"])
            
            p_final = Image.new("RGBA", target_size, (0,0,0,0))
            p_final.paste(p_bg, (0,0), p_mask)
            p_final.paste(p_img, (0,0), p_mask)
            
            px_final = int(px+1 * scale - (target_size[0]-ps_w)//2)
            py_final = self.overrides.get("player_1_y" if index==1 else "player_2_y", py//scale) * scale
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

    def draw_nesine_area_tiny(self, frame, box_bounds, ho_bounds, scale):
        bx, by, bw, bh = box_bounds
        hx, hy, hw, hh = ho_bounds
        draw = ImageDraw.Draw(frame)
        
        # Yellow Box
        # Updated to #fbc600 for brand consistency
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(251, 198, 0, 255))
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA").resize((45, 23), Image.Resampling.LANCZOS)
            # Center logo in yellow area or use exact PSD: (7, 14)
            frame.alpha_composite(n_img, (7, 14))
            
        # Hemen Oyna
        # Use specialized 300x50 asset for maximum sharpness (Native 60x19)
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "templates", "hemen_oyna_300x50.png")
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA")
            frame.alpha_composite(ho_img, (int(hx), int(hy)))

    def save_gif_standard(self, frames, filename, durations):
        """Standard GIF output for 300x50."""
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        combined = Image.new("RGB", (frames[0].width * len(frames), frames[0].height))
        for i, f in enumerate(frames): combined.paste(f, (i * frames[0].width, 0))
        palette = combined.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
        p_frames = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
        p_frames[0].save(out_path, save_all=True, append_images=p_frames[1:], duration=durations, loop=0, optimize=False, disposal=2)
        return out_path
