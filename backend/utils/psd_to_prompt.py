import os
import json
from psd_tools import PSDImage
from pathlib import Path

def extract_psd_metadata(psd_path):
    print(f"Bölümleniyor: {psd_path}")
    psd = PSDImage.open(psd_path)
    
    metadata = {
        "filename": os.path.basename(psd_path),
        "size": {
            "width": psd.width,
            "height": psd.height
        },
        "layers": []
    }
    
    def walk_layers(layers, result_list):
        for layer in layers:
            layer_info = {
                "name": layer.name,
                "top": layer.top,
                "left": layer.left,
                "width": layer.width,
                "height": layer.height,
                "kind": layer.kind,
                "visible": layer.visible
            }
            
            if hasattr(layer, 'text') and layer.text:
                layer_info["text"] = layer.text
                # Font detaylarını çekmeye çalış
                try:
                    from psd_tools.constants import Resource
                    if layer.kind == 'type':
                        res = layer.resource_dict.get(Resource.TEXT_DATA)
                        if res:
                            layer_info["font_family"] = str(layer.fontset) if hasattr(layer, 'fontset') else "Unknown"
                except:
                    pass
            
            result_list.append(layer_info)
            
            # Eğer grup ise alt katmanları da gez
            if layer.is_group():
                walk_layers(layer, result_list)
                
    walk_layers(psd, metadata["layers"])
    return metadata

def process_all_samples(samples_dir, output_dir):
    samples_path = Path(samples_dir)
    output_path = Path(output_dir)
    
    if not samples_path.exists():
        print(f"Hata: {samples_dir} klasörü bulunamadı.")
        return

    # Tüm alt klasörleri gez
    for psd_file in samples_path.rglob("*.psd"):
        # Klasör yapısını koru
        relative_path = psd_file.relative_to(samples_path)
        league_name = relative_path.parts[0]
        
        league_output = output_path / league_name
        league_output.mkdir(parents=True, exist_ok=True)
        
        data = extract_psd_metadata(str(psd_file))
        
        # Çıktı dosya adı ölçü bazlı olsun
        size_name = f"{data['size']['width']}x{data['size']['height']}"
        file_id = psd_file.stem
        output_file = league_output / f"{size_name}_{file_id}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Tamamlandı: {output_file}")

if __name__ == "__main__":
    SAMPLES_DIR = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples"
    OUTPUT_DIR = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts"
    process_all_samples(SAMPLES_DIR, OUTPUT_DIR)
