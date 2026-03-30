import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .ziraat_base import ZiraatBase

class Ziraat320(ZiraatBase):
    def render(self, data):
        """Golden Ziraat 320x100 (Restored from d1fce013 v23)."""
        width, height = 320, 100
        rgb_frames = []
        scenes = ["320x100_1.json", "320x100_2.json", "320x100_3.json"]
        
        # Sahne bazlı WHITELIST (PSD'deki rastgele visibility'yi ezmek için)
        scene_roles = {
            1: ["Bg", "ztk-yatay-logo", "BANT"],
            2: ["Bg", "Futbolcu", "Logoları", "HEMEN OYNA", "BANT"],
            3: ["Bg", "Beşiktaş", "-", "Gün_saat", "BANT", "HEMEN OYNA"]
        }

        for scene_idx, scene_file in enumerate(scenes):
            scene_id = scene_idx + 1
            prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "prompts", "ziraat", scene_file)
            with open(prompt_path, "r", encoding="utf-8") as f:
                scene_data = json.load(f)
            
            frame = Image.new("RGBA", (width, height), (214, 0, 28, 255))
            draw = ImageDraw.Draw(frame)
            whitelist = scene_roles[scene_id]
            
            for layer in scene_data["layers"]:
                name = layer["name"]
                pos = (layer["left"], layer["top"])
                l_w, l_h = layer["width"], layer["height"]
                
                # Role-Based Filtering
                if not any(role in name for role in whitelist): continue
                
                # 1. Background
                if name == "Bg":
                    bg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bg_320x100_clean.png")
                    if os.path.exists(bg_path): frame.paste(Image.open(bg_path).convert("RGBA"), (0, 0))
                
                # 2. Ziraat Logo (Scene 1 only)
                elif "ztk-yatay-logo" in name:
                    z_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ztk_yatay_logo.png")
                    if os.path.exists(z_path):
                        z_img = Image.open(z_path).convert("RGBA")
                        frame.alpha_composite(z_img, pos)
                
                # 3. Oyuncular (Scene 2 only)
                elif "Futbolcu" in name:
                    p_idx = 1 if layer["left"] < 160 else 2
                    p_path = data.get(f"player_{p_idx}_path")
                    if p_path and os.path.exists(p_path):
                        p_size = (l_w, l_h); p_img_src = Image.open(p_path).convert("RGBA")
                        p_img = ImageOps.fit(p_img_src, p_size, Image.Resampling.LANCZOS, centering=(0.5, 0.0))
                        p_mask = self.create_player_mask(p_size, radii=(max(30, l_h//2), 15, 15, 15))
                        color = self.get_team_colors(data.get(f"team_{p_idx}"))["p"]
                        o_size = (p_size[0]+4, p_size[1]+4); o_mask = self.create_player_mask(o_size, (max(32, o_size[1]//2), 17, 17, 17))
                        frame.paste(Image.new("RGBA", o_size, color), (pos[0]-2, pos[1]-2), o_mask)
                        p_final = Image.new("RGBA", p_size, (0,0,0,0)); p_final.paste(p_img, (0,0), p_mask); frame.alpha_composite(p_final, pos)
                
                # 4. Takım Logoları (Scene 2 only)
                elif "Logoları" in name:
                    l_idx = 1 if layer["left"] < 160 else 2
                    l_path = data.get(f"logo_{l_idx}_path")
                    if l_path and os.path.exists(l_path):
                        l_img = Image.open(l_path).convert("RGBA"); l_img.thumbnail((l_w, l_h), Image.Resampling.LANCZOS)
                        frame.alpha_composite(l_img, (pos[0]+(l_w-l_img.width)//2, pos[1]+(l_h-l_img.height)//2))
                
                # 5. Yazılar (Scene 3 only)
                elif "-" in name or "Beşiktaş" in name: 
                    font = ImageFont.truetype(self.font_bold, 26)
                    t1, t2 = data.get("team_1").upper(), data.get("team_2").upper()
                    draw.text((pos[0] + (l_w - draw.textlength(t1, font))//2, pos[1]), t1, font=font, fill="black")
                    draw.text((pos[0] + (l_w - draw.textlength(t2, font))//2, pos[1] + 32), t2, font=font, fill="black")
                
                elif "Gün_saat" in name:
                    font = ImageFont.truetype(self.font_reg, 18)
                    hour, day = data.get('hour').upper(), data.get('day').upper()
                    draw.text((pos[0] + l_w - draw.textlength(hour, font), pos[1]), hour, font=font, fill="black")
                    draw.text((pos[0] + l_w - draw.textlength(day, font), pos[1] + 25), day, font=font, fill="black")
 
                # 6. Branding
                elif "BANT" in name:
                    b_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "nesine_320x100_bant.png")
                    ho_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "hemen_oyna_320x100.png")
                    if scene_id == 1:
                        if os.path.exists(b_path): frame.alpha_composite(Image.open(b_path).convert("RGBA"), pos)
                    elif scene_id == 2:
                        if os.path.exists(b_path): frame.alpha_composite(Image.open(b_path).convert("RGBA"), (129, 68))
                    elif scene_id == 3:
                        if os.path.exists(b_path) and os.path.exists(ho_path):
                            frame.alpha_composite(Image.open(b_path).convert("RGBA"), (95, 68))
                            frame.alpha_composite(Image.open(ho_path).convert("RGBA"), (163, 69))
 
                elif "HEMEN OYNA" in name and scene_id == 2:
                    h_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "hemen_oyna_320x100.png")
                    if os.path.exists(h_path): frame.alpha_composite(Image.open(h_path).convert("RGBA"), (129, 43))
            
            rgb_frames.append(frame.convert("RGB"))
 
        # Quantize and Save GIF
        combined = Image.new("RGB", (width*len(rgb_frames), height))
        for i, f in enumerate(rgb_frames): combined.paste(f, (i*width, 0))
        palette = combined.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
        p_frames = [img.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for img in rgb_frames]
        
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "banner_320x100.gif")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        p_frames[0].save(out_path, save_all=True, append_images=p_frames[1:], duration=[2000, 3500, 2500], loop=0, optimize=False, disposal=2)
        return out_path
