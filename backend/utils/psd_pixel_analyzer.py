import os
from psd_tools import PSDImage
from PIL import Image
import numpy as np

def analyze_pixels(psd_path, output_dir):
    psd = PSDImage.open(psd_path)
    os.makedirs(output_dir, exist_ok=True)
    
    analysis_results = []
    
    # Hedef katman isimleri (veya bir kısmını içeren isimler)
    targets = ["Gün_saat", "Gaziantep FK - Fenerbahçe"]
    
    for layer in psd.descendants():
        if layer.name in targets:
            print(f"Analiz ediliyor: {layer.name}")
            # Katmanı PNG olarak kaydet
            image = layer.composite()
            if image:
                img_path = os.path.join(output_dir, f"{layer.name}.png")
                image.save(img_path)
                
                # Piksel analizi (Renk ve Boyut)
                img = np.array(image.convert("RGBA"))
                # Alpha kanalı > 0 olan pikselleri bul
                non_transparent = np.where(img[:, :, 3] > 0)
                
                if len(non_transparent[0]) > 0:
                    y_min, y_max = np.min(non_transparent[0]), np.max(non_transparent[0])
                    x_min, x_max = np.min(non_transparent[1]), np.max(non_transparent[1])
                    
                    # Ortalama renk (Alpha > 0 olanlar için)
                    pixels = img[non_transparent]
                    avg_color = np.mean(pixels[:, :3], axis=0).astype(int)
                    hex_color = '#{:02x}{:02x}{:02x}'.format(*avg_color)
                    
                    analysis_results.append({
                        "layer": layer.name,
                        "pixel_height": int(y_max - y_min),
                        "pixel_width": int(x_max - x_min),
                        "suggested_font_size": int(y_max - y_min), # Kabaca yükseklik = font size
                        "color_hex": hex_color
                    })
                    
    return analysis_results

if __name__ == "__main__":
    PSD_FILE = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/ziraat/1200x628_png/1.psd"
    OUTPUT = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat/pixel_analysis"
    results = analyze_pixels(PSD_FILE, OUTPUT)
    
    with open(os.path.join(OUTPUT, "results.json"), "w", encoding="utf-8") as f:
        import json
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"Analiz tamamlandı: {OUTPUT}/results.json")
