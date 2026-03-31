import os
from PIL import Image
from ..base import BaseLayout

class UEFA300_50(BaseLayout):
    def render(self, data):
        """UEFA 300x50 Animated GIF Banner (Step 2: Branding Scenes)."""
        width, height = 300, 50
        
        # 1. Generate 3 Frames (Scenes) with specific branding
        frame1 = self.render_scene_1(data, width, height)
        frame2 = self.render_scene_2(data, width, height)
        frame3 = self.render_scene_3(data, width, height)
        
        output_dir = os.path.join(os.path.dirname(__file__), "../../../output")
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, "banner_uefa_300_50.gif")
        
        # Save as Animated GIF: 2 seconds per frame (2000ms)
        frame1.save(out_path, save_all=True, append_images=[frame2, frame3], duration=2000, loop=0)
        
        return out_path

    def get_base_canvas(self, width, height):
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        # Use the specific user-provided background
        bg_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/300x50/300x50_bg.png"
        if os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGBA")
            canvas.alpha_composite(bg, (0,0))
        return canvas

    def draw_nesine(self, canvas):
        path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/300x50/300x50_nesine.png"
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            canvas.alpha_composite(img, (0,0))

    def draw_uefa(self, canvas):
        path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/300x50/300x50_uefa_logo.png"
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            canvas.alpha_composite(img, (0,0))

    def draw_hemen_oyna(self, canvas):
        path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/uefa/300x50/300x50_hemen_oyna.png"
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            canvas.alpha_composite(img, (0,0))

    def render_scene_1(self, data, w, h):
        """Scene 1: Nesine + 2-Line Title."""
        canvas = self.get_base_canvas(w, h)
        self.draw_nesine(canvas)
        
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(canvas)
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        title = data.get('match_title', '').upper()
        
        if title:
            # Short format: 24px Saira (Larger as requested)
            font_title = ImageFont.truetype(f_saira, 24)
            words = title.split()
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            
            # Center title in the right-ish area
            # At 24px, we need tight vertical spacing
            draw.text((185, 14), line1, font=font_title, fill="white", anchor="mm", align="center")
            draw.text((185, 36), line2, font=font_title, fill="white", anchor="mm", align="center")
            
        return canvas

    def render_scene_2(self, data, w, h):
        """Scene 2: Nesine + UEFA + Hemen Oyna + Teams + Info."""
        canvas = self.get_base_canvas(w, h)
        self.draw_nesine(canvas)
        self.draw_uefa(canvas) # In the middle approx
        self.draw_hemen_oyna(canvas) # Far right (same as Scene 3)
        
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(canvas)
        # Using Saira UltraCondensed-Bold as per PSD Screenshot metadata (approx)
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        
        # 1. Match Info (Center-right of the UEFA logo)
        # Size: 17.18px from PSD screenshot
        # Only first letter capitalized for day name
        day = data.get('day', '').capitalize()
        hour = data.get('hour', '')
        font_info = ImageFont.truetype(f_saira, 17)
        
        # Colors: Green (#06BF50) for Day, White for Hour
        # Shifted left for better balance: 168 instead of 175
        draw.text((168, 15), day, font=font_info, fill="#06BF50", anchor="mm")
        draw.text((168, 35), hour, font=font_info, fill="white", anchor="mm")
        
        # 2. Team Logos (Beside the text block)
        l1_path = data.get('logo_1_path')
        l2_path = data.get('logo_2_path')
        glow_color = (6, 191, 80, 140) # Visible/Tight green glow
        
        if l1_path and os.path.exists(l1_path):
            l1 = Image.open(l1_path).convert("RGBA")
            # Enlarge: 40px instead of 30px
            l1.thumbnail((40, 40), Image.Resampling.LANCZOS)
            # Add Glow to Logos
            self.draw_mask_glow(canvas, l1, (120, 25), color=glow_color, dilation=1, blur=1)
            # Closer: 175 - 55 = 120
            canvas.alpha_composite(l1, (120 - l1.width//2, 25 - l1.height//2))
            
        if l2_path and os.path.exists(l2_path):
            l2 = Image.open(l2_path).convert("RGBA")
            # Enlarge: 40px instead of 30px
            l2.thumbnail((40, 40), Image.Resampling.LANCZOS)
            # Further left: 208 instead of 215
            self.draw_mask_glow(canvas, l2, (208, 25), color=glow_color, dilation=1, blur=1)
            canvas.alpha_composite(l2, (208 - l2.width//2, 25 - l2.height//2))
            
        return canvas

    def render_scene_3(self, data, w, h):
        """Scene 3: Players + Day/Hour + Branding (Smaller & Higher)."""
        canvas = self.get_base_canvas(w, h)
        
        # 1. Players (Drawn first)
        p1_path = data.get('player_1_path')
        p2_path = data.get('player_2_path')
        glow_color = (6, 191, 80, 140) # More prominent (high opacity)
        
        if p1_path and os.path.exists(p1_path):
            p1 = Image.open(p1_path).convert("RGBA")
            p1.thumbnail((105, 105), Image.Resampling.LANCZOS)
            # Prominent but Tight Glow (Dilation 1, Blur 1)
            self.draw_mask_glow(canvas, p1, (125, 4 + p1.height//2), color=glow_color, dilation=1, blur=1)
            canvas.alpha_composite(p1, (125 - p1.width//2, 4))
            
        if p2_path and os.path.exists(p2_path):
            p2 = Image.open(p2_path).convert("RGBA")
            p2.thumbnail((95, 95), Image.Resampling.LANCZOS)
            # Further left: 208 instead of 215
            self.draw_mask_glow(canvas, p2, (208, 4 + p2.height//2), color=glow_color, dilation=1, blur=1)
            canvas.alpha_composite(p2, (208 - p2.width//2, 4))
        
        # 2. Branding (Top Layer)
        self.draw_nesine(canvas)
        self.draw_uefa(canvas)
        self.draw_hemen_oyna(canvas)
        
        # 3. Match Info (Center-right of the UEFA logo)
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(canvas)
        f_saira = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/fonts/uefa/Saira_UltraCondensed-Bold.ttf"
        # Only first letter capitalized for day name
        day = data.get('day', '').capitalize()
        hour = data.get('hour', '')
        font_info = ImageFont.truetype(f_saira, 17)
        
        draw.text((168, 15), day, font=font_info, fill="#06BF50", anchor="mm")
        draw.text((168, 35), hour, font=font_info, fill="white", anchor="mm")
            
        return canvas
