import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat320(ZiraatBase):
    def render(self, data):
        """Refined Ziraat 320x100 GIF (Ground Truth PSD Coordinates)."""
        width, height = 320, 100
        rgb_frames = []
        scenes = ["320x100_1.json", "320x100_2.json", "320x100_3.json"]
        
        for scene_idx, scene_file in enumerate(scenes):
            scene_id = scene_idx + 1
            frame = Image.new("RGBA", (width, height), (240, 240, 240, 255))
            draw = ImageDraw.Draw(frame)
            
            # Global Background
            bg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bg_320x100_clean.png")
            if os.path.exists(bg_path):
                 frame.paste(Image.open(bg_path).convert("RGBA"), (0, 0))

            if scene_id == 1:
                self.draw_scene_1(frame, data)
            elif scene_id == 2:
                self.draw_scene_2(frame, data)
            elif scene_id == 3:
                self.draw_scene_3(frame, data)
            
            # Persistent Branding (Scene 1 only - centered)
            if scene_id == 1:
                self.draw_nesine_area_gt(frame, (129, 68, 60, 42), (137, 72, 45, 23))
            
            rgb_frames.append(frame.convert("RGB"))

        # GIF Generation
        output_path = self.save_gif_optimized(rgb_frames, "banner_320x100.gif", durations=[2000, 3500, 4000])
        return output_path

    def draw_scene_1(self, frame, data):
        """Scene 1: Ziraat Logo only (No Hemen Oyna)."""
        # PSD Ground Truth: (84, 8) with size 150x58
        z_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
        if os.path.exists(z_path):
            z_img = Image.open(z_path).convert("RGBA")
            # Exact PSD scale
            z_img = z_img.resize((150, 58), Image.Resampling.LANCZOS)
            frame.alpha_composite(z_img, (84, 8))

    def draw_scene_2(self, frame, data):
        """Scene 2: Players with Logos and Side-by-Side Branding."""
        # Side-by-side Players (Pill masks)
        self.draw_player_with_logo(frame, data, 1, (9, 3, 64, 87), (68, 24, 55, 55))
        self.draw_player_with_logo(frame, data, 2, (243, 3, 64, 87), (200, 24, 55, 55))
        
        # Refined Side-by-Side Branding (Nesine + Hemen Oyna)
        self.draw_nesine_area_gt(frame, (95, 68, 60, 42), (103, 72, 45, 23))
        self.draw_hemen_oyna_badge(frame, (163, 70, 62, 20))

    def draw_scene_3(self, frame, data):
        """Scene 3: Refined 2x2 Grid with Side-by-Side Branding."""
        draw = ImageDraw.Draw(frame)
        t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
        hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
        
        # Dynamic Scaling Helper
        def get_font_scaled(text, base_size, max_w, font_path):
            s = base_size
            f = ImageFont.truetype(font_path, s)
            while draw.textlength(text, font=f) > max_w and s > 12:
                s -= 1
                f = ImageFont.truetype(font_path, s)
            return f

        # Column 1 (X=10): Teams (Max width reduced to accommodate branding)
        f_team1 = get_font_scaled(t1, 18, 100, self.font_bold)
        f_team2 = get_font_scaled(t2, 18, 100, self.font_bold)
        draw.text((10, 12), t1, font=f_team1, fill="black")
        draw.text((10, 42), t2, font=f_team2, fill="black")
        
        # Column 2 (X=245): Match Info
        f_hour = get_font_scaled(hour, 18, 70, self.font_bold)
        f_day = get_font_scaled(day, 14, 70, self.font_reg)
        draw.text((245, 12), hour, font=f_hour, fill="black")
        draw.text((245, 42), day, font=f_day, fill="black")

        # Refined Side-by-Side Branding (Nesine Left, Hemen Oyna Right)
        self.draw_nesine_area_gt(frame, (110, 68, 60, 42), (118, 72, 45, 23))
        self.draw_hemen_oyna_badge(frame, (175, 70, 62, 20))

    def draw_player_with_logo(self, frame, data, index, p_bounds, l_bounds):
        px, py, pw, ph = p_bounds
        lx, ly, lw, lh = l_bounds
        t_colors = self.get_team_colors(data.get(f"team_{index}"))
        p_path = data.get(f"player_{index}_path")
        
        # Yellow Frame
        draw = ImageDraw.Draw(frame)
        draw.rectangle([px, py, px+pw, py+ph], outline=(252, 215, 0, 255), width=2)
        
        if p_path and os.path.exists(p_path):
            # Pill Mask Logic
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), (pw-4, ph-4), Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_mask = self.create_player_mask((pw-4, ph-4), radii=(max(30, ph//2), 10, 10, 10))
            p_bg = Image.new("RGBA", (pw-4, ph-4), t_colors["p"])
            
            p_final = Image.new("RGBA", (pw-4, ph-4), (0,0,0,0))
            p_final.paste(p_bg, (0,0), p_mask)
            p_final.paste(p_img, (0,0), p_mask)
            frame.alpha_composite(p_final, (px+2, py+2))

        # Logo Parity
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            l_img.thumbnail((lw, lh), Image.Resampling.LANCZOS)
            clx = lx + (lw - l_img.width)//2
            cly = ly + (lh - l_img.height)//2
            frame.alpha_composite(l_img, (clx, cly))

    def draw_nesine_area_gt(self, frame, box_bounds, logo_bounds):
        bx, by, bw, bh = box_bounds
        lx, ly, lw, lh = logo_bounds
        draw = ImageDraw.Draw(frame)
        
        # Nesine Yellow Box (PSD: 129, 68, 60x42)
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(252, 215, 0, 255))
        
        # Nesine Logo (PSD: 137, 72, 45x23)
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            # Exact PSD scale
            n_img = n_img.resize((lw, lh), Image.Resampling.LANCZOS)
            frame.alpha_composite(n_img, (lx, ly))

    def draw_hemen_oyna_badge(self, frame, bounds):
        hx, hy, hw, hh = bounds
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "hemen_oyna_320x100.png")
        if os.path.exists(ho_path):
            # Exact PSD scale: 62x20
            ho_img = Image.open(ho_path).convert("RGBA").resize((hw, hh), Image.Resampling.LANCZOS)
            frame.alpha_composite(ho_img, (hx, hy))

    def save_gif_optimized(self, frames, filename, durations):
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        combined = Image.new("RGB", (frames[0].width * len(frames), frames[0].height))
        for i, f in enumerate(frames): combined.paste(f, (i * frames[0].width, 0))
        palette = combined.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
        p_frames = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
        p_frames[0].save(out_path, save_all=True, append_images=p_frames[1:], duration=durations, loop=0, optimize=False, disposal=2)
        return out_path
