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
            # Nesine Area (0, 0, 66, 50) and Hemen Oyna (228, 10, 62, 30)
            self.draw_nesine_area_tiny(img, (0, 0, 66, 50), (228, 10, 62, 30), 1)

            if scene_id == 1:
                # Ziraat Logo (centered in the remaining middle space [66, 228])
                z_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
                if os.path.exists(z_path):
                    z_img = Image.open(z_path).convert("RGBA")
                    z_img.thumbnail((120, 35), Image.Resampling.LANCZOS)
                    cx = 66 + (228 - 66 - z_img.width)//2
                    img.alpha_composite(z_img, (int(cx), (sh - z_img.height)//2))
                
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
        """Micro Side-by-side Players and Logos."""
        self.draw_player_micro(frame, data, 1, (75 * scale, 2 * scale, 38 * scale, 48 * scale), (115 * scale, 10 * scale, 35 * scale, 35 * scale), scale)
        self.draw_player_micro(frame, data, 2, (150 * scale, 2 * scale, 38 * scale, 48 * scale), (190 * scale, 10 * scale, 35 * scale, 35 * scale), scale)

    def draw_scene_3(self, frame, data, scale):
        """Match Info Grid shifted for Left Branding."""
        draw = ImageDraw.Draw(frame)
        t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
        hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
        
        try:
            f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
            f_team = ImageFont.truetype(self.font_bold, int(14 * scale))
            f_info = ImageFont.truetype(f_saira, int(12 * scale))
            
            # Left after Nesine (X=75)
            draw.text((75 * scale, 5 * scale), t1, font=f_team, fill="black")
            draw.text((75 * scale, 25 * scale), t2, font=f_team, fill="black")
            
            # Right before Hemen Oyna (X=170)
            draw.text((170 * scale, 7 * scale), hour, font=f_team, fill="black")
            draw.text((170 * scale, 27 * scale), day, font=f_info, fill="#06BF50")
        except: pass

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
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), (ps_w, ps_h), Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_mask = self.create_player_mask((ps_w, ps_h), radii=(10 * scale, 5 * scale, 5 * scale, 5 * scale))
            p_bg = Image.new("RGBA", (ps_w, ps_h), t_colors["p"])
            
            p_final = Image.new("RGBA", (ps_w, ps_h), (0,0,0,0))
            p_final.paste(p_bg, (0,0), p_mask)
            p_final.paste(p_img, (0,0), p_mask)
            frame.alpha_composite(p_final, (int(px+1 * scale), int(py+1 * scale)))

        # Logo Parity (Equal resize)
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            l_img.thumbnail((lw, lh), Image.Resampling.LANCZOS)
            clx = lx + (lw - l_img.width)//2
            cly = ly + (lh - l_img.height)//2
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
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((int(bw-6 * scale), int(bh-4 * scale)), Image.Resampling.LANCZOS)
            frame.alpha_composite(n_img, (int(bx + (bw - n_img.width)//2), int(by + (bh - n_img.height)//2)))
            
        # Hemen Oyna
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "hemen_oyna_320x100.png")
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((int(hw), int(hh)), Image.Resampling.LANCZOS)
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
