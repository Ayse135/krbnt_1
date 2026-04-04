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
        
        # Post-Processing: Downsample & Sharpen
        def post_process(img):
            img = img.resize((sw, sh), Image.Resampling.LANCZOS)
            from PIL import ImageFilter
            return img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))

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
            
            # Persistent Branding (Scene 1 only - centered)
            if scene_id == 1:
                self.draw_nesine_area_gt(frame, (129 * scale, 68 * scale, 60 * scale, 42 * scale), (137 * scale, 72 * scale, 45 * scale, 23 * scale), scale)
            
            rgb_frames.append(post_process(frame).convert("RGB"))

        # GIF Generation
        output_path = self.save_gif_optimized(rgb_frames, "banner_320x100.gif", durations=[2000, 3500, 4000])
        return output_path

    def draw_scene_1(self, frame, data, scale):
        """Scene 1: Ziraat Logo only (No Hemen Oyna)."""
        z_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
        if os.path.exists(z_path):
            z_img = Image.open(z_path).convert("RGBA")
            z_img = z_img.resize((150 * scale, 58 * scale), Image.Resampling.LANCZOS)
            frame.alpha_composite(z_img, (84 * scale, 8 * scale))

    def draw_scene_2(self, frame, data, scale):
        """Scene 2: Players with Logos and Side-by-Side Branding."""
        self.draw_player_with_logo(frame, data, 1, (9 * scale, 3 * scale, 64 * scale, 87 * scale), (68 * scale, 24 * scale, 55 * scale, 55 * scale), scale)
        self.draw_player_with_logo(frame, data, 2, (243 * scale, 3 * scale, 64 * scale, 87 * scale), (200 * scale, 24 * scale, 55 * scale, 55 * scale), scale)
        
        self.draw_nesine_area_gt(frame, (95 * scale, 68 * scale, 60 * scale, 42 * scale), (103 * scale, 72 * scale, 45 * scale, 23 * scale), scale)
        self.draw_hemen_oyna_badge(frame, (163 * scale, 70 * scale, 62 * scale, 20 * scale), scale)

    def draw_scene_3(self, frame, data, scale):
        """Scene 3: Refined 2x2 Grid with Side-by-Side Branding."""
        draw = ImageDraw.Draw(frame)
        t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
        hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
        
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        
        # Dynamic Scaling Helper
        def get_font_scaled(text, base_size, max_w, font_path):
            s = base_size
            f = ImageFont.truetype(font_path, int(s * scale))
            while draw.textlength(text, font=f) > max_w * scale and s > 12:
                s -= 1
                f = ImageFont.truetype(font_path, int(s * scale))
            return f

        # Column 1 (X=10): Teams
        f_team1 = get_font_scaled(t1, 18, 100, self.font_bold)
        f_team2 = get_font_scaled(t2, 18, 100, self.font_bold)
        draw.text((10 * scale, 12 * scale), t1, font=f_team1, fill="black")
        draw.text((10 * scale, 42 * scale), t2, font=f_team2, fill="black")
        
        # Column 2 (X=245): Match Info (Using Saira for Info)
        f_hour = get_font_scaled(hour, 18, 70, f_saira)
        f_day = get_font_scaled(day, 14, 70, f_saira)
        draw.text((245 * scale, 12 * scale), hour, font=f_hour, fill="black")
        draw.text((245 * scale, 42 * scale), day, font=f_day, fill="#06BF50")

        # Refined Side-by-Side Branding
        self.draw_nesine_area_gt(frame, (110 * scale, 68 * scale, 60 * scale, 42 * scale), (118 * scale, 72 * scale, 45 * scale, 23 * scale), scale)
        self.draw_hemen_oyna_badge(frame, (175 * scale, 70 * scale, 62 * scale, 20 * scale), scale)

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
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), (ps_w, ps_h), Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_mask = self.create_player_mask((ps_w, ps_h), radii=(max(30 * scale, ph//2), 10 * scale, 10 * scale, 10 * scale))
            p_bg = Image.new("RGBA", (ps_w, ps_h), t_colors["p"])
            
            p_final = Image.new("RGBA", (ps_w, ps_h), (0,0,0,0))
            p_final.paste(p_bg, (0,0), p_mask)
            p_final.paste(p_img, (0,0), p_mask)
            frame.alpha_composite(p_final, (int(px+2 * scale), int(py+2 * scale)))

        # Logo Parity
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            l_img.thumbnail((lw, lh), Image.Resampling.LANCZOS)
            clx = lx + (lw - l_img.width)//2
            cly = ly + (lh - l_img.height)//2
            frame.alpha_composite(l_img, (clx, cly))

    def draw_nesine_area_gt(self, frame, box_bounds, logo_bounds, scale):
        bx, by, bw, bh = box_bounds
        lx, ly, lw, lh = logo_bounds
        draw = ImageDraw.Draw(frame)
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(252, 215, 0, 255))
        
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
