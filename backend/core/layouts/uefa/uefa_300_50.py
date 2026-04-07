import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..base import BaseLayout

class UEFA300_50(BaseLayout):
    def render(self, data):
        """UEFA 300x50 Animated GIF Banner with Supersampling (2x)."""
        sw, sh = 300, 50
        scale = 2
        width, height = sw * scale, sh * scale
        
        # 1. Generate 3 Frames (Scenes) at 2x resolution
        frame1 = self.render_scene_1(data, width, height, scale)
        frame2 = self.render_scene_2(data, width, height, scale)
        frame3 = self.render_scene_3(data, width, height, scale)
        
        # 2. Downsample and Sharpen each frame + Add Branding at 1x
        def post_process(img, scene_id):
            img = img.resize((sw, sh), Image.Resampling.LANCZOS)
            from PIL import ImageFilter
            # Apply subtle sharpening to restore clarity after downsampling
            img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
            
            # Draw branding at 1x for maximum sharpness
            self.draw_nesine(img, scale=1)
            if scene_id != 1:
                self.draw_uefa(img, scale=1)
                self.draw_hemen_oyna(img, scale=1)
                
            return img.convert("RGB")

        f1 = post_process(frame1, 1)
        f2 = post_process(frame2, 2)
        f3 = post_process(frame3, 3)
        
        output_dir = os.path.join(os.path.dirname(__file__), "../../../output")
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, "banner_uefa_300_50.gif")
        
        # Save as Animated GIF: 2 seconds per frame (2000ms)
        f1.save(out_path, save_all=True, append_images=[f2, f3], duration=2000, loop=0)
        
        return out_path

    def get_base_canvas(self, width, height):
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        # Use the specific user-provided background
        bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/300x50/300x50_bg.png"
        if os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGBA")
            if bg.size != (width, height):
                bg = bg.resize((width, height), Image.Resampling.LANCZOS)
            canvas.alpha_composite(bg, (0,0))
        return canvas

    def draw_nesine(self, canvas, scale=1):
        path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/300x50/300x50_nesine.png"
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            if scale != 1:
                img = img.resize((canvas.width, canvas.height), Image.Resampling.LANCZOS)
            canvas.alpha_composite(img, (0,0))

    def draw_uefa(self, canvas, scale=1):
        path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/300x50/300x50_uefa_logo.png"
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            if scale != 1:
                img = img.resize((canvas.width, canvas.height), Image.Resampling.LANCZOS)
            canvas.alpha_composite(img, (0,0))

    def draw_hemen_oyna(self, canvas, scale=1):
        path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/300x50/300x50_hemen_oyna.png"
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            if scale != 1:
                img = img.resize((canvas.width, canvas.height), Image.Resampling.LANCZOS)
            canvas.alpha_composite(img, (0,0))

    def render_scene_1(self, data, w, h, scale):
        """Scene 1: Nesine + 2-Line Title."""
        canvas = self.get_base_canvas(w, h)
        # Branding is now handled in post_process (1x scale)
        
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(canvas)
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        title = data.get('match_title', '').upper()
        
        if title:
            # Short format: 24px Saira (Larger as requested)
            font_title = ImageFont.truetype(f_saira, 24 * scale)
            words = title.split()
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            
            # Dynamic Position & Scale
            mt_fs = self.overrides.get("match_title_fs", 24)
            font_title = ImageFont.truetype(f_saira, int(mt_fs * scale))
            tx = (self.overrides.get("match_title_x", self.overrides.get("title_x", 185)) + int(self.overrides.get("match_title_x_offset", 0))) * scale
            ty = (self.overrides.get("match_title_y", self.overrides.get("title_y", 25)) + int(self.overrides.get("match_title_y_offset", 0))) * scale
            draw.text((tx, ty - 11 * scale), line1, font=font_title, fill="white", anchor="mm", align="center")
            draw.text((tx, ty + 11 * scale), line2, font=font_title, fill="white", anchor="mm", align="center")
            
        return canvas

    def render_scene_2(self, data, w, h, scale):
        """Scene 2: Nesine + UEFA + Hemen Oyna + Teams + Info."""
        canvas = self.get_base_canvas(w, h)
        # Branding is now handled in post_process (1x scale)
        
        draw = ImageDraw.Draw(canvas)
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        
        day = data.get('day', '').capitalize()
        hour = data.get('hour', '')
        font_info = ImageFont.truetype(f_saira, 17 * scale)
        
        draw.text((168 * scale, 15 * scale), day, font=font_info, fill="#06BF50", anchor="mm")
        draw.text((168 * scale, 35 * scale), hour, font=font_info, fill="white", anchor="mm")
        
        # 2. Team Logos
        l1_path = data.get('logo_1_path')
        l2_path = data.get('logo_2_path')
        glow_color = (6, 191, 80, 140)
        
        if l1_path and os.path.exists(l1_path):
            l1 = Image.open(l1_path).convert("RGBA")
            l1_scale = float(self.overrides.get("logo_1_scale", 1.0))
            l1.thumbnail((int(40 * scale * l1_scale), int(40 * scale * l1_scale)), Image.Resampling.LANCZOS)
            
            l1_x = (120 + int(self.overrides.get("logo_1_x_offset", 0))) * scale
            l1_y = (25 + int(self.overrides.get("logo_y_offset", 0))) * scale
            self.draw_mask_glow(canvas, l1, (l1_x, l1_y), color=glow_color, dilation=1 * scale, blur=1 * scale)
            canvas.alpha_composite(l1, (int(l1_x - l1.width//2), int(l1_y - l1.height//2)))
            
        if l2_path and os.path.exists(l2_path):
            l2 = Image.open(l2_path).convert("RGBA")
            l2_scale = float(self.overrides.get("logo_2_scale", 1.0))
            l2.thumbnail((int(40 * scale * l2_scale), int(40 * scale * l2_scale)), Image.Resampling.LANCZOS)
            
            l2_x = (208 + int(self.overrides.get("logo_2_x_offset", 0))) * scale
            l2_y = (25 + int(self.overrides.get("logo_y_offset", 0))) * scale
            self.draw_mask_glow(canvas, l2, (l2_x, l2_y), color=glow_color, dilation=1 * scale, blur=1 * scale)
            canvas.alpha_composite(l2, (int(l2_x - l2.width//2), int(l2_y - l2.height//2)))
            
        return canvas

    def render_scene_3(self, data, w, h, scale):
        """Scene 3: Players + Day/Hour + Branding."""
        canvas = self.get_base_canvas(w, h)
        draw = ImageDraw.Draw(canvas)
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        
        day = data.get('day', '').capitalize()
        hour = data.get('hour', '')
        
        # 1. Players
        p1_path = data.get('player_1_path')
        p2_path = data.get('player_2_path')
        glow_color = (6, 191, 80, 140)
        
        if p1_path and os.path.exists(p1_path):
            p1 = Image.open(p1_path).convert("RGBA")
            p1_scale = self.overrides.get("player_1_scale", self.overrides.get("player_scale", 1.0))
            p1.thumbnail((int(105 * scale * p1_scale), int(105 * scale * p1_scale)), Image.Resampling.LANCZOS)
            p1_y = self.overrides.get("player_1_y", 4) * scale
            self.draw_mask_glow(canvas, p1, (125 * scale, p1_y + p1.height//2), color=glow_color, dilation=1 * scale, blur=1 * scale)
            canvas.alpha_composite(p1, (int(125 * scale - p1.width//2), int(p1_y)))
            
        if p2_path and os.path.exists(p2_path):
            p2 = Image.open(p2_path).convert("RGBA")
            p2_scale = self.overrides.get("player_2_scale", self.overrides.get("player_scale", 1.0))
            p2.thumbnail((int(95 * scale * p2_scale), int(95 * scale * p2_scale)), Image.Resampling.LANCZOS)
            p2_y = self.overrides.get("player_2_y", 4) * scale
            self.draw_mask_glow(canvas, p2, (208 * scale, p2_y + p2.height//2), color=glow_color, dilation=1 * scale, blur=1 * scale)
            canvas.alpha_composite(p2, (int(208 * scale - p2.width//2), int(p2_y)))
        
        # 3. Match Info: Time (17px) Day (17px) or overrides
        fs_info = self.overrides.get("match_info_fs", 17)
        font_info = ImageFont.truetype(f_saira, fs_info * scale)
        
        info_x = (self.overrides.get("match_info_x", 168) + int(self.overrides.get("match_info_x_offset", 0))) * scale
        day_y = (self.overrides.get("day_y", 15) + int(self.overrides.get("match_info_y_offset", 0))) * scale
        hour_y = (self.overrides.get("hour_y", 35) + int(self.overrides.get("match_info_y_offset", 0))) * scale
        
        draw.text((info_x, day_y), day, font=font_info, fill="#06BF50", anchor="mm")
        draw.text((info_x, hour_y), hour, font=font_info, fill="white", anchor="mm")
            
        return canvas
