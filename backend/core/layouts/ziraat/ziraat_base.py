import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageChops
from ..base import BaseLayout

class ZiraatBase(BaseLayout):
    def __init__(self, engine):
        super().__init__(engine)
        self.font_bold = self.fonts["ziraat_bold"]
        self.font_reg = self.fonts["ziraat_reg"]

    def draw_dynamic_backdrop(self, canvas, bounds, primary_color, secondary_color, scale):
        """Standard High-Quality Ziraat Backdrop with dynamic team colors."""
        bx, by, bw, bh = bounds
        mask_size = (int(bw), int(bh))
        
        # 1. Load Templates
        asset_dir = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/ziraat/players_canvas"
        wave_asset = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/assets/templates/backdrop_waves_v3.png"
        
        def load_tinted(path, color):
            if not os.path.exists(path): return None
            img = Image.open(path).convert("RGBA").resize(mask_size, Image.Resampling.LANCZOS)
            # Create color overlay layer
            color_layer = Image.new("RGBA", mask_size, color)
            # Multiply for true tinting (Photoshop Color Overlay logic)
            tinted = ImageChops.multiply(img, color_layer)
            return tinted

        # 2. Render Layers
        # A. Base Fill (Primary Color)
        base_fill = load_tinted(os.path.join(asset_dir, "shape2.png"), primary_color)
        
        # B. Waves (Secondary Color)
        # Using waves as a tintable layer
        waves = Image.open(wave_asset).convert("RGBA").resize(mask_size, Image.Resampling.LANCZOS)
        sec_color_layer = Image.new("RGBA", mask_size, secondary_color)
        waves_tinted = ImageChops.multiply(waves, sec_color_layer)
        
        # C. Hollow Outline (Primary Color - for accent)
        outline = load_tinted(os.path.join(asset_dir, "shape1.png"), primary_color)

        # 3. Composite with Blending Logic
        # Start with Base Fill
        backdrop = Image.new("RGBA", mask_size, (0,0,0,0))
        if base_fill: backdrop.paste(base_fill, (0,0))
        
        # Apply Waves (Overlay style)
        if waves_tinted:
            # Mask waves to base shape using shape2 alpha
            mask = Image.open(os.path.join(asset_dir, "shape2.png")).convert("L").resize(mask_size, Image.Resampling.LANCZOS)
            backdrop.paste(waves_tinted, (0,0), mask)
            
        # Apply Light Burst (Additive / Linear Dodge)
        # We take the grayscale burst and ADD it to the backdrop
        burst_mask = waves.split()[3] # Use alpha channel of waves for burst intensity or separate
        # Linear Dodge simulation: backdrop = convert(min(backdrop + white, 255))
        light_layer = waves.convert("RGB") # The white parts of waves
        backdrop_rgb = backdrop.convert("RGB")
        # PIL Add with 1.0 scale is Linear Dodge
        added = ImageChops.add(backdrop_rgb, light_layer, scale=1.0, offset=0)
        
        # Restore Alpha
        backdrop = Image.merge("RGBA", (
            added.split()[0], added.split()[1], added.split()[2],
            mask # Final clipping mask
        ))
        
        # 4. Final Outline and Placement
        if outline: backdrop.alpha_composite(outline)
        
        canvas.alpha_composite(backdrop, (int(bx), int(by)))

    def generate_glitch_texture(self, size, color):
        """Surgical radial burst streaks (Premium Glitch) for ZIRAAT"""
        texture = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(texture)
        w, h = size
        cx, cy = w // 2, h // 2
        num_streaks = 60
        for _ in range(num_streaks):
            angle = random.uniform(0, 360)
            rad = math.radians(angle)
            start_dist = random.uniform(0, w * 0.2)
            length = random.uniform(w * 0.4, w * 0.9)
            width_val = random.uniform(1, 4)
            opacity = random.randint(20, 150)
            x0 = cx + math.cos(rad) * start_dist
            y0 = cy + math.sin(rad) * start_dist
            points = [(x0, y0)]
            for d in range(int(start_dist) + 10, int(start_dist + length), 20):
                jitter = random.uniform(-10, 10)
                px = cx + math.cos(rad) * d + math.cos(rad + math.pi/2) * jitter
                py = cy + math.sin(rad) * d + math.sin(rad + math.pi/2) * jitter
                points.append((px, py))
            if len(points) > 1:
                draw.line(points, fill=(color[0], color[1], color[2], opacity), width=int(width_val))
        return texture.filter(ImageFilter.GaussianBlur(radius=1))
