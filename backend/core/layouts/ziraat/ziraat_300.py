import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat300(ZiraatBase):
    def render(self, data):
        """Refined Ziraat 300x50 GIF (Ground Truth Persistent Branding)."""
        width, height = 300, 50
        rgb_frames = []
        
        # Scenes Logic
        for scene_id in [1, 2, 3]:
            frame = Image.new("RGBA", (width, height), (240, 240, 240, 255))
            draw = ImageDraw.Draw(frame)
            
            # Global Background (Short)
            bg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bg_300x50_clean.png")
            if os.path.exists(bg_path):
                 frame.paste(Image.open(bg_path).convert("RGBA"), (0, 0))

            if scene_id == 1:
                self.draw_scene_1(frame, data)
            elif scene_id == 2:
                self.draw_scene_2(frame, data)
            elif scene_id == 3:
                self.draw_scene_3(frame, data)
            
            # Persistent Branding (Absolute Bottom-Center across all frames)
            # In 50px height, we'll put it at Y=28 to leave room for some top content or center it.
            # Actually, the user says "tüm sahnelerde nesine logosu ve sarı alan olcak".
            # Consistent Branding across all frames (Nesine on LEFT, Hemen Oyna on RIGHT)
            self.draw_nesine_area_tiny(frame, (0, 0, 66, 50), (228, 10, 62, 30))
            
            rgb_frames.append(frame.convert("RGB"))

        # Save GIF
        output_path = self.save_gif_standard(rgb_frames, "banner_300x50.gif", durations=[2000, 3500, 4000])
        return output_path

    def draw_scene_1(self, frame, data):
        """Ziraat Horizontal Logo (Centered in remaining space)."""
        z_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
        if os.path.exists(z_path):
            z_img = Image.open(z_path).convert("RGBA")
            # Larger scale for 300x50
            z_img.thumbnail((120, 35), Image.Resampling.LANCZOS)
            # Center between Nesine (X=66) and Hemen Oyna (X=230)
            cx = 66 + (230 - 66 - z_img.width)//2
            frame.alpha_composite(z_img, (cx, (frame.height - z_img.height)//2))

    def draw_scene_2(self, frame, data):
        """Micro Side-by-side Players and Logos."""
        # Left Player (75, 2), Right Player (150, 2)
        self.draw_player_micro(frame, data, 1, (75, 2, 38, 48), (115, 10, 35, 35))
        self.draw_player_micro(frame, data, 2, (150, 2, 38, 48), (190, 10, 35, 35))

    def draw_scene_3(self, frame, data):
        """Match Info Grid shifted for Left Branding."""
        draw = ImageDraw.Draw(frame)
        t1, t2 = data.get("team_1", "TEAM 1").upper(), data.get("team_2", "TEAM 2").upper()
        hour, day = data.get("hour", "20:30"), data.get("day", "PAZARTESİ").upper()
        
        try:
            f_team = ImageFont.truetype(self.font_bold, 14)
            f_info = ImageFont.truetype(self.font_reg, 12)
            
            # Left after Nesine (X=75)
            draw.text((75, 5), t1, font=f_team, fill="black")
            draw.text((75, 25), t2, font=f_team, fill="black")
            
            # Right before Hemen Oyna (X=170)
            draw.text((170, 7), hour, font=f_team, fill="black")
            draw.text((170, 27), day, font=f_info, fill="black")
        except: pass

    def draw_player_micro(self, frame, data, index, bounds, logo_bounds):
        px, py, pw, ph = bounds
        lx, ly, lw, lh = logo_bounds
        t_colors = self.get_team_colors(data.get(f"team_{index}"))
        p_path = data.get(f"player_{index}_path")
        
        draw = ImageDraw.Draw(frame)
        # Micro frame
        draw.rectangle([px, py, px+pw, py+ph], outline=(252, 215, 0, 255), width=1)
        
        if p_path and os.path.exists(p_path):
            p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), (pw-2, ph-2), Image.Resampling.LANCZOS, centering=(0.5, 0.0))
            p_mask = self.create_player_mask((pw-2, ph-2), radii=(10, 5, 5, 5))
            p_bg = Image.new("RGBA", (pw-2, ph-2), t_colors["p"])
            
            p_final = Image.new("RGBA", (pw-2, ph-2), (0,0,0,0))
            p_final.paste(p_bg, (0,0), p_mask)
            p_final.paste(p_img, (0,0), p_mask)
            frame.alpha_composite(p_final, (px+1, py+1))

        # Logo Parity (Equal resize)
        l_path = data.get(f"logo_{index}_path")
        if l_path and os.path.exists(l_path):
            l_img = Image.open(l_path).convert("RGBA")
            l_img.thumbnail((lw, lh), Image.Resampling.LANCZOS)
            clx = lx + (lw - l_img.width)//2
            cly = ly + (lh - l_img.height)//2
            frame.alpha_composite(l_img, (clx, cly))

    def draw_nesine_area_tiny(self, frame, box_bounds, ho_bounds):
        bx, by, bw, bh = box_bounds
        hx, hy, hw, hh = ho_bounds
        draw = ImageDraw.Draw(frame)
        
        # Yellow Box
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(252, 215, 0, 255))
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            n_img.thumbnail((bw-6, bh-4), Image.Resampling.LANCZOS)
            frame.alpha_composite(n_img, (bx + (bw - n_img.width)//2, by + (bh - n_img.height)//2))
            
        # Hemen Oyna
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "hemen_oyna_320x100.png")
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((hw, hh), Image.Resampling.LANCZOS)
            frame.alpha_composite(ho_img, (hx, hy))

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
