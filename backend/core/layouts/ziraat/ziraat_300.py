import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat300(ZiraatBase):
    def render(self, data):
        """Golden Ziraat 300x50 (Restored from d1fce013 v23)."""
        width, height = 300, 50
        bg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bg_300x50_clean.png")
        rgb_frames = []
        
        # --- SAHNE 1 ---
        frame1 = Image.open(bg_path).convert("RGBA") if os.path.exists(bg_path) else Image.new("RGBA", (width, height), (214, 0, 28, 255))
        z_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
        if os.path.exists(z_path):
            z_logo = Image.open(z_path).convert("RGBA").resize((90, 35), Image.Resampling.LANCZOS)
            frame1.paste(z_logo, (70, 7), z_logo)
        bant_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "nesine_320x100_bant.png")
        if os.path.exists(bant_path):
            bant = Image.open(bant_path).convert("RGBA").resize((40, 28), Image.Resampling.LANCZOS)
            frame1.paste(bant, (180, 11), bant)
        rgb_frames.append(frame1.convert("RGB"))
        
        # --- SAHNE 2 ---
        frame2 = Image.open(bg_path).convert("RGBA") if os.path.exists(bg_path) else Image.new("RGBA", (width, height), (214, 0, 28, 255))
        p_size = (38, 48)
        anchors = [(5, 2), (257, 2)]
        for i in [1, 2]:
            p_path = data.get(f"player_{i}_path")
            px, py = anchors[i-1]
            color = self.get_team_colors(data.get(f"team_{i}"))["p"]
            o_size = (p_size[0] + 2, p_size[1] + 2)
            o_mask = self.create_player_mask(o_size, radii=(8, 8, 8, 8))
            frame2.paste(Image.new("RGBA", o_size, color), (px - 1, py - 1), o_mask)
            if p_path and os.path.exists(p_path):
                p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), p_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                p_mask = self.create_player_mask(p_size, radii=(8, 8, 8, 8))
                p_final = Image.new("RGBA", p_size, (0,0,0,0)); p_final.paste(p_img, (0,0), p_mask); frame2.paste(p_final, (px, py), p_final)
        
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "hemen_oyna_320x100.png")
        if os.path.exists(ho_path):
            ho = Image.open(ho_path).convert("RGBA").resize((45, 15), Image.Resampling.LANCZOS)
            frame2.paste(ho, (127, 8), ho)
        if os.path.exists(bant_path):
            bant = Image.open(bant_path).convert("RGBA").resize((40, 28), Image.Resampling.LANCZOS)
            frame2.paste(bant, (130, 25), bant)
        rgb_frames.append(frame2.convert("RGB"))
        
        # --- SAHNE 3 ---
        frame3 = Image.open(bg_path).convert("RGBA") if os.path.exists(bg_path) else Image.new("RGBA", (width, height), (214, 0, 28, 255))
        draw3 = ImageDraw.Draw(frame3)
        font_main = ImageFont.truetype(self.font_bold, 10)
        font_sub = ImageFont.truetype(self.font_reg, 9)
        t1, t2 = data.get('team_1').upper(), data.get('team_2').upper()
        draw3.text((6, 11), t1, font=font_main, fill="black")
        draw3.text((6, 27), t2, font=font_main, fill="black")
        hour, day = data.get('hour').upper(), data.get('day').upper()
        draw3.text((294 - draw3.textlength(hour, font_main), 11), hour, font=font_main, fill="black")
        draw3.text((294 - draw3.textlength(day, font_sub), 27), day, font=font_sub, fill="black")
        
        # Side-by-side Branding
        tw = 40 + 5 + 45
        sx = (width - tw) // 2
        if os.path.exists(bant_path): frame3.paste(Image.open(bant_path).convert("RGBA").resize((40, 28)), (sx, 11))
        if os.path.exists(ho_path): frame3.paste(Image.open(ho_path).convert("RGBA").resize((45, 15)), (sx + 45, 17))
        rgb_frames.append(frame3.convert("RGB"))

        # Save GIF
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_300x50.gif")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        rgb_frames[0].save(out_path, save_all=True, append_images=rgb_frames[1:], duration=[2000, 3500, 2500], loop=0)
        return out_path
