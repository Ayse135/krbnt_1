import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageMath, ImageChops
from ..base import BaseLayout

class UEFA320_100(BaseLayout):
    def render(self, data):
        """UEFA 320x100 Animated GIF Banner Generation with Supersampling (2x)."""
        sw, sh = 320, 100
        scale = 2
        width, height = sw * scale, sh * scale
        
        # 1. Generate 3 Frames (Scenes) at 2x resolution
        frame1 = self.render_scene_1(data, width, height, scale)
        frame2 = self.render_scene_2(data, width, height, scale)
        frame3 = self.render_scene_3(data, width, height, scale)
        
        # 2. Downsample and Sharpen each frame + Add Branding at 1x
        def post_process(img, scene_id):
            img = img.resize((sw, sh), Image.Resampling.LANCZOS)
            # Apply subtle sharpening to restore clarity after downsampling
            img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
            
            # Draw branding at 1x for maximum sharpness
            show_ho = scene_id != 1
            self.draw_branding(img, show_hemen_oyna=show_ho, scale=1)
            
            return img.convert("RGB")

        f1 = post_process(frame1, 1)
        f2 = post_process(frame2, 2)
        f3 = post_process(frame3, 3)
        
        output_dir = os.path.join(os.path.dirname(__file__), "../../../output")
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, "banner_uefa_320_100.gif")
        
        # Save as Animated GIF: 2 seconds per frame (2000ms)
        f1.save(out_path, save_all=True, append_images=[f2, f3], duration=2000, loop=0)
        
        return out_path

    def get_base_canvas(self, width, height):
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        # Use the specific user-provided background
        bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/320x100_gif/320x100_bg.png"
        if os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGBA")
            # Scale background to current canvas resolution
            bg = bg.resize((width, height), Image.Resampling.LANCZOS)
            canvas.alpha_composite(bg, (0,0))
        return canvas

    def render_scene_1(self, data, w, h, scale):
        """Scene 1: Match Title Focus (2 Lines)."""
        canvas = self.get_base_canvas(w, h)
        # Branding is now handled in post_process (1x scale)
        
        # 1. Match Title (Centered, 2 Lines)
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        title = data.get('match_title', '').upper()
        if title:
            # Saira fontu için daha büyük boyut (Max Visibility)
            font_title = ImageFont.truetype(f_saira, 30 * scale)
            draw = ImageDraw.Draw(canvas)
            
            # Kelimelere göre bölme
            words = title.split()
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            
            # Nesine logosunu dengelemek için hafif sağa offsetli (170) ama daha ortalı görünüm
            draw.text((170 * scale, h/2 - 15 * scale), line1, font=font_title, fill="white", anchor="mm", align="center")
            draw.text((170 * scale, h/2 + 15 * scale), line2, font=font_title, fill="white", anchor="mm", align="center")
            
        return canvas

    def draw_branding(self, canvas, show_hemen_oyna=True, scale=1):
        """Step 2: Precise Branding Alignment (Specialized 320x100 PNGs)."""
        # Specialized Nesine Logo (Full-frame 320x100)
        n_logo_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/320x100_gif/320x100_nesine.png"
        if os.path.exists(n_logo_path):
            n_img = Image.open(n_logo_path).convert("RGBA")
            if scale != 1:
                n_img = n_img.resize((canvas.width, canvas.height), Image.Resampling.LANCZOS)
            canvas.alpha_composite(n_img, (0, 0))
        
        # Specialized Hemen Oyna Badge (Full-frame 320x100)
        if show_hemen_oyna:
            h_badge_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/320x100_gif/320x100_hemen_oyna.png"
            if os.path.exists(h_badge_path):
                h_img = Image.open(h_badge_path).convert("RGBA")
                if scale != 1:
                    h_img = h_img.resize((canvas.width, canvas.height), Image.Resampling.LANCZOS)
                canvas.alpha_composite(h_img, (0, 0))

    def render_scene_2(self, data, w, h, scale):
        """Scene 2: Team Logos Focus."""
        canvas = self.get_base_canvas(w, h)
        
        # 1. Team Logos (Drawn first so Branding stays on top)
        logo1_path = data.get('logo_1_path')
        logo2_path = data.get('logo_2_path')
        
        if logo1_path and os.path.exists(logo1_path):
            l1 = Image.open(logo1_path).convert("RGBA")
            l1.thumbnail((60 * scale, 60 * scale), Image.Resampling.LANCZOS)
            self.draw_mask_glow(canvas, l1, (110 * scale, 45 * scale), color=(6, 191, 80, 230), dilation=6 * scale, blur=15 * scale)
            canvas.alpha_composite(l1, (110 * scale - l1.width//2, 45 * scale - l1.height//2))
            
        if logo2_path and os.path.exists(logo2_path):
            l2 = Image.open(logo2_path).convert("RGBA")
            l2.thumbnail((60 * scale, 60 * scale), Image.Resampling.LANCZOS)
            self.draw_mask_glow(canvas, l2, (210 * scale, 45 * scale), color=(6, 191, 80, 230), dilation=6 * scale, blur=15 * scale)
            canvas.alpha_composite(l2, (210 * scale - l2.width//2, 45 * scale - l2.height//2))
        
        # 3. Match Info (Center)
        self.draw_match_info_center(canvas, data, scale)
            
        return canvas

    def render_scene_3(self, data, w, h, scale):
        """Scene 3: Players Focus (Precise face/neck alignment)."""
        canvas = self.get_base_canvas(w, h)
        
        # 1. Players (Drawn before Branding so logos stay on top)
        p1_path = data.get('player_1_path')
        p2_path = data.get('player_2_path')
        
        if p1_path and os.path.exists(p1_path):
            p1 = Image.open(p1_path).convert("RGBA")
            p1.thumbnail((140 * scale, 140 * scale), Image.Resampling.LANCZOS)
            self.draw_mask_glow(canvas, p1, (100 * scale, 18 * scale + p1.height//2), color=(6, 191, 80, 180), dilation=5 * scale, blur=15 * scale)
            canvas.alpha_composite(p1, (100 * scale - p1.width//2, 18 * scale))
            
        if p2_path and os.path.exists(p2_path):
            p2 = Image.open(p2_path).convert("RGBA")
            p2.thumbnail((140 * scale, 140 * scale), Image.Resampling.LANCZOS)
            self.draw_mask_glow(canvas, p2, (222 * scale, 15 * scale + p2.height//2), color=(6, 191, 80, 180), dilation=5 * scale, blur=15 * scale)
            canvas.alpha_composite(p2, (222 * scale - p2.width//2, 15 * scale))
        
        # 3. Match Info (Center)
        self.draw_match_info_center(canvas, data, scale)
            
        return canvas

    def draw_match_info_center(self, canvas, data, scale):
        draw = ImageDraw.Draw(canvas)
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        u_logo_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/frontend/public/assets/branding/uefa_logo.png"
        
        day = data.get('day', '').capitalize()
        hour = data.get('hour', '')
        
        font_320 = ImageFont.truetype(f_saira, 18 * scale)
        # Day
        draw.text((160 * scale, 25 * scale), day, font=font_320, fill="#06BF50", anchor="mm")
        # Hour
        draw.text((160 * scale, 48 * scale), hour, font=font_320, fill="white", anchor="mm")
        
        # UEFA Logo (Bottom center)
        if os.path.exists(u_logo_path):
            u_img = Image.open(u_logo_path).convert("RGBA")
            u_img.thumbnail((30 * scale, 40 * scale), Image.Resampling.LANCZOS)
            canvas.alpha_composite(u_img, ((canvas.width - u_img.width) // 2, 60 * scale))

    def draw_mask_glow(self, canvas, img, center, color, dilation=15, blur=30, intensity=1.5):
        margin = blur + 20
        glow_canvas = Image.new("RGBA", (img.width + margin*2, img.height + margin*2), (0,0,0,0))
        alpha = img.split()[3]
        def force_odd(n):
            n = max(1, int(n))
            return n if n % 2 != 0 else n + 1
        ambient_mask = alpha.filter(ImageFilter.MaxFilter(force_odd(dilation)))
        outer_glow = Image.merge("RGBA", (
            Image.new("L", img.size, color[0]), Image.new("L", img.size, color[1]), Image.new("L", img.size, color[2]),
            ambient_mask
        ))
        glow_canvas.paste(outer_glow, (margin, margin), outer_glow)
        glow_canvas = glow_canvas.filter(ImageFilter.GaussianBlur(blur))
        r, g, b, a = glow_canvas.split()
        a = a.point(lambda i: min(255, int(i * (intensity * (color[3]/255.0))))) 
        glow_canvas = Image.merge("RGBA", (r, g, b, a))
        canvas.alpha_composite(glow_canvas, (int(center[0] - glow_canvas.width//2), int(center[1] - glow_canvas.height//2)))
