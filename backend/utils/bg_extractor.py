from psd_tools import PSDImage
import os
from pathlib import Path

def extract_bgs(psd_samples_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    samples_path = Path(psd_samples_dir)
    
    for psd_file in samples_path.rglob("*.psd"):
        try:
            print(f"İşleniyor: {psd_file.name}")
            psd = PSDImage.open(str(psd_file))
            # 'Bg' katmanını bul (Büyük/Küçük harf duyarsız)
            bg_layers = [l for l in psd.descendants() if l.name.lower() == 'bg']
            
            if bg_layers:
                # En üstteki 'Bg' katmanını al
                bg_layer = bg_layers[0]
                img = bg_layer.composite()
                output_path = os.path.join(output_dir, f"bg_{psd_file.stem}.png")
                img.save(output_path)
                print(f"Kaydedildi: {output_path}")
            else:
                print(f"Hata: {psd_file.name} içinde 'Bg' katmanı bulunamadı.")
        except Exception as e:
            print(f"Hata ({psd_file.name}): {str(e)}")

if __name__ == "__main__":
    SAMPLES = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/ziraat/1200x628_png"
    OUTPUT = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_audit"
    extract_bgs(SAMPLES, OUTPUT)
