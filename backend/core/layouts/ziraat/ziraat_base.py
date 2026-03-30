import math
import random
from PIL import Image, ImageDraw, ImageFilter
from ..base import BaseLayout

class ZiraatBase(BaseLayout):
    def __init__(self, engine):
        super().__init__(engine)
        self.font_bold = self.fonts["ziraat_bold"]
        self.font_reg = self.fonts["ziraat_reg"]

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
