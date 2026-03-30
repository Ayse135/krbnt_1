import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat120(ZiraatBase):
    def render(self, data):
        """Golden Ziraat 120x600 (Restored from d1fce013 v23)."""
        width, height = 120, 600
        canvas = Image.new("RGBA", (width, height), (214, 0, 28, 255))
        
        # 1. Background
        bg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bg_120x600_clean.png")
        if os.path.exists(bg_path): canvas.paste(Image.open(bg_path).convert("RGBA"), (0, 0))
        
        # 2. Ziraat Logo (Top)
        z_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "ztk_yatay_logo.png")
        if os.path.exists(z_logo_path):
            z_img = Image.open(z_logo_path).convert("RGBA").resize((41, 54), Image.Resampling.LANCZOS)
            canvas.alpha_composite(z_img, (41, 28))

        # 3. Oyuncular (Pill Mask)
        p_y = 163
        p_size = (57, 77)
        for i in [1, 2]:
            p_x = 2 if i == 1 else 61
            p_path = data.get(f"player_{i}_path")
            color = self.get_team_colors(data.get(f"team_{i}"))["p"]
            o_size = (p_size[0] + 6, p_size[1] + 6)
            o_mask = self.create_player_mask(o_size, radii=(22, 22, 22, 22))
            canvas.paste(Image.new("RGBA", o_size, color), (p_x - 3, p_y - 3), o_mask)
            if p_path and os.path.exists(p_path):
                p_img = ImageOps.fit(Image.open(p_path).convert("RGBA"), p_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                p_mask = self.create_player_mask(p_size, radii=(20, 20, 20, 20))
                p_final = Image.new("RGBA", p_size, (0,0,0,0)); p_final.paste(p_img, (0, 0), p_mask); canvas.alpha_composite(p_final, (p_x, p_y))

        # 4. Takım Logoları
        l_y = 229
        for i in [1, 2]:
            l_path = data.get(f"logo_{i}_path")
            l_x, l_size = (13 if i == 1 else 69), (36, 42) if i == 1 else (43, 43)
            if l_path and os.path.exists(l_path):
                l_img = Image.open(l_path).convert("RGBA"); l_img.thumbnail(l_size, Image.Resampling.LANCZOS)
                canvas.alpha_composite(l_img, (l_x + (l_size[0]-l_img.width)//2, l_y + (l_size[1]-l_img.height)//2))

        # 5. Yazılar (Typography)
        draw = ImageDraw.Draw(canvas)
        font_teams = ImageFont.truetype(self.font_bold, 16)
        font_info = ImageFont.truetype(self.font_reg, 12)
        font_time = ImageFont.truetype(self.font_reg, 18)
        target_w, center_x = 110, 60
        self.draw_text_with_spacing(draw, data.get('team_1', '').upper(), (center_x - target_w//2, 309), font_teams, fill="black", target_width=target_w)
        self.draw_text_with_spacing(draw, data.get('team_2', '').upper(), (center_x - target_w//2, 330), font_teams, fill="black", target_width=target_w)
        self.draw_text_with_spacing(draw, data.get('hour', '').upper(), (center_x - target_w//2, 372), font_time, fill="black", target_width=target_w)
        self.draw_text_with_spacing(draw, data.get('day', '').upper(), (center_x - target_w//2, 395), font_info, fill="black", target_width=target_w)

        # 6. Bottom Branding
        ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "hemen_oyna_320x100.png")
        if os.path.exists(ho_path):
            ho_img = Image.open(ho_path).convert("RGBA").resize((83, 25), Image.Resampling.LANCZOS)
            canvas.alpha_composite(ho_img, (19, 460))
        y_box_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "nesine_yellow_box.png")
        if os.path.exists(y_box_path):
            y_box = Image.open(y_box_path).convert("RGBA").resize((133, 70), Image.Resampling.LANCZOS)
            canvas.alpha_composite(y_box, (-5, 542))
        z_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "branding", "ziraat_logo.png")
        if not os.path.exists(z_logo_path):
            z_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
        n_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "branding", "nesine_logo.png")
        if os.path.exists(n_logo_path):
            n_logo = Image.open(n_logo_path).convert("RGBA").resize((78, 38), Image.Resampling.LANCZOS)
            canvas.alpha_composite(n_logo, (22, 549))

        # Save Output
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_120x600.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        canvas.save(out_path)
        return out_path
