from psd_tools import PSDImage
import os

def extract_clean_bg(psd_path, output_path):
    print(f"PSD açılıyor: {psd_path}")
    psd = PSDImage.open(psd_path)
    
    # Tüm katmanları görünmez yap
    for layer in psd:
        layer.visible = False
        
    # Sadece 'Bg' katmanını görünür yap
    bg_layers = [l for l in psd.descendants() if l.name.lower() == 'bg']
    if bg_layers:
        bg_layer = bg_layers[0]
        bg_layer.visible = True
        # Parent grup varsa onu da görünür yap (recursive)
        parent = bg_layer.parent
        while parent and parent != psd:
            parent.visible = True
            parent = parent.parent
            
        # Tüm canvas'ın kompozitini al (Bu sayede maske/efektler uygulanır)
        img = psd.composite()
        img.save(output_path)
        print(f"Temiz BG kaydedildi: {output_path}")
    else:
        print("Hata: Bg katmanı bulunamadı")

if __name__ == "__main__":
    # 1.psd, 2.psd ve 3.psd'yi dene
    for i in [1, 2, 3]:
        src = f"/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/ziraat/1200x628_png/{i}.psd"
        out = f"/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/backend/bg_clean_{i}.png"
        extract_clean_bg(src, out)
