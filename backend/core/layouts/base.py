import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps

class BaseLayout:
    def __init__(self, engine):
        self.engine = engine
        self.fonts = engine.fonts

    def get_team_colors(self, team_name):
        """Takım renklerini döner (Primary, Secondary)"""
        colors = {
            "BEŞİKTAŞ": {"p": (0, 0, 0, 255), "s": (255, 255, 255, 255)},
            "GALATASARAY": {"p": (214, 0, 28, 255), "s": (252, 215, 0, 255)},
            "FENERBAHÇE": {"p": (0, 35, 71, 255), "s": (252, 215, 0, 255)},
            "TRABZONSPOR": {"p": (161, 30, 53, 255), "s": (0, 149, 218, 255)},
            "BAŞAKŞEHİR": {"p": (255, 102, 0, 255), "s": (0, 0, 128, 255)},
            "ANTALYASPOR": {"p": (255, 0, 0, 255), "s": (255, 255, 255, 255)},
            "RİZESPOR": {"p": (0, 107, 63, 255), "s": (255, 255, 255, 255)},
            "SAMSUNSPOR": {"p": (255, 0, 0, 255), "s": (255, 255, 255, 255)},
            "EYÜPSPOR": {"p": (128, 0, 128, 255), "s": (255, 255, 0, 255)}
        }
        return colors.get(team_name.upper(), {"p": (214, 0, 28, 255), "s": (255, 255, 255, 255)})

    def create_player_mask(self, size, radii=(180, 40, 40, 40)):
        """Piller maskesi - Her köşe için ayrı radius desteği (TL, TR, BR, BL)"""
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        w, h = size
        r_tl, r_tr, r_br, r_bl = radii
        draw.pieslice([0, 0, 2*r_tl, 2*r_tl], 180, 270, fill=255)
        draw.pieslice([w-2*r_tr, 0, w, 2*r_tr], 270, 0, fill=255)
        draw.pieslice([w-2*r_br, h-2*r_br, w, h], 0, 90, fill=255)
        draw.pieslice([0, h-2*r_bl, 2*r_bl, h], 90, 180, fill=255)
        draw.rectangle([r_tl, 0, w-r_tr, max(r_tl, r_tr)], fill=255)
        draw.rectangle([0, max(r_tl, r_tr), w, h-max(r_bl, r_br)], fill=255)
        draw.rectangle([r_bl, h-max(r_bl, r_br), w-r_br, h], fill=255)
        return mask

    def draw_text_with_spacing(self, draw, text, position, font, fill="white", spacing=0, target_width=None):
        """Metni belirli bir harf aralığı ile veya belirli bir genişliğe yayarak çizer"""
        x, y = position
        current_x = x
        if target_width:
            total_chars_width = sum(draw.textlength(c, font=font) for c in text)
            if len(text) > 1:
                spacing = (target_width - total_chars_width) / (len(text) - 1)
        for char in text:
            draw.text((current_x, y), char, font=font, fill=fill)
            current_x += draw.textlength(char, font=font) + spacing

    def _colorize_image(self, image_rgba, color):
        """RGBA bir görüntüyü tinting (çarpma) yöntemiyle renklendirir, detayları korur"""
        if image_rgba.mode != "RGBA":
            image_rgba = image_rgba.convert("RGBA")
        r, g, b, a = image_rgba.split()
        cr, cg, cb = color[0]/255.0, color[1]/255.0, color[2]/255.0
        new_r = r.point(lambda i: int(i * cr))
        new_g = g.point(lambda i: int(i * cg))
        new_b = b.point(lambda i: int(i * cb))
        return Image.merge("RGBA", (new_r, new_g, new_b, a))

    def render(self, data):
        raise NotImplementedError("Layout classes must implement render(data)")
