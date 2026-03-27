from psd_tools import PSDImage
import os

def extract_surgical_bg(psd_path, output_path):
    print(f"Surgical extraction: {psd_path}")
    psd = PSDImage.open(psd_path)
    
    # Hide all layers recursively
    def hide_all(layers):
        for l in layers:
            l.visible = False
            if l.is_group():
                hide_all(l)
    
    hide_all(psd)
    
    found = False
    def show_bg_and_parents(layer):
        # Katmanın kendisini göster
        layer.visible = True
        # Varsa parent'larını da göster
        curr = layer.parent
        while curr and not isinstance(curr, PSDImage):
            curr.visible = True
            curr = curr.parent

    found = False
    def find_bg(layers):
        nonlocal found
        for l in layers:
            if l.name.lower() == 'bg':
                show_bg_and_parents(l)
                found = True
                return
            if l.is_group():
                find_bg(l)
    
    find_bg(psd)
    
    if found:
        # Composite the whole PSD (renders the canvas)
        img = psd.composite()
        img.save(output_path)
        print(f"PSD composite ile BG hazır: {output_path}")
    else:
        print(f"UYARI: 'Bg' bulunamadı, boş composite kaydediliyor.")
        psd.composite().save(output_path)

def extract_layer(psd_path, layer_name, output_path):
    print(f"Extracting layer '{layer_name}' from: {psd_path}")
    psd = PSDImage.open(psd_path)
    found = False
    def walk(layers):
        nonlocal found
        for l in layers:
            if l.name.lower() == layer_name.lower():
                l.composite().save(output_path)
                found = True
                return
            if l.is_group():
                walk(l)
            if found: return
    walk(psd)
    if found:
        print(f"Katman başarıyla kaydedildi: {output_path}")
    else:
        print(f"UYARI: '{layer_name}' katmanı bulunamadı!")

def extract_nesine_yellow_box(psd_path, output_path):
    psd = PSDImage.open(psd_path)
    # Nesine Logo -> Rectangle 7 or LOGO RECTANGLE copy
    target_names = ["rectangle", "shape", "logo rectangle"]
    
    found = False
    def walk(layers):
        nonlocal found
        for l in layers:
            if any(n in l.name.lower() for n in target_names):
                l.composite().save(output_path)
                print(f"Sarı kutu çıkarıldı: {output_path}")
                found = True
                return
            if l.is_group():
                walk(l)
            if found: return

    walk(psd)

if __name__ == "__main__":
    # Paths
    BASE_DIR = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok"
    BACKEND_DIR = os.path.join(BASE_DIR, "backend")
    
    SRC_1200 = os.path.join(BASE_DIR, "psd_samples/ziraat/1200x628_png/1.psd")
    SRC_120 = os.path.join(BASE_DIR, "psd_samples/ziraat/120x600_png/1.psd")
    SRC_320 = os.path.join(BASE_DIR, "psd_samples/ziraat/320x100_gif/1.psd")
    
    # 1. Backrounds
    extract_surgical_bg(SRC_1200, os.path.join(BACKEND_DIR, "bg_ultra_clean.png"))
    extract_surgical_bg(SRC_120, os.path.join(BACKEND_DIR, "bg_120x600_clean.png"))
    extract_surgical_bg(SRC_320, os.path.join(BACKEND_DIR, "bg_320x100_clean.png"))
    
    # 2. Logos & Branding
    extract_nesine_yellow_box(SRC_1200, os.path.join(BACKEND_DIR, "nesine_yellow_box.png"))
    extract_layer(SRC_320, "ztk-yatay-logo", os.path.join(BACKEND_DIR, "ztk_yatay_logo.png"))
    
    # Nesine logo extraction from 320x100 'BANT' group if needed
    # (Actually we can use the existing logo or extract the whole BANT group for scene 3)
    extract_layer(SRC_320, "BANT", os.path.join(BACKEND_DIR, "nesine_320x100_bant.png"))
