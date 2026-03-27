import json
import os
from pathlib import Path

def compare_psds(json_files):
    all_data = []
    for f in json_files:
        with open(f, "r", encoding="utf-8") as j:
            all_data.append(json.load(j))
            
    if not all_data:
        return None
        
    # İlk dosyayı baz alarak her katmanı kontrol et
    base_layers = all_data[0]["layers"]
    master_prompt = {
        "size": all_data[0]["size"],
        "constants": [],
        "variables": {}
    }
    
    for i, base_layer in enumerate(base_layers):
        name = base_layer["name"]
        is_variable = False
        values = []
        
        for data in all_data:
            # Aynı indeksteki veya aynı isimdeki katmanı bul (indeks daha güvenli)
            current_layer = data["layers"][i]
            val = current_layer.get("text", current_layer["name"])
            values.append(val)
            
        # Eğer değerler değişiyorsa değişkendir
        if len(set(values)) > 1:
            is_variable = True
            
        layer_meta = {
            "name": name,
            "top": base_layer["top"],
            "left": base_layer["left"],
            "width": base_layer["width"],
            "height": base_layer["height"],
            "kind": base_layer["kind"]
        }
        
        if is_variable:
            # Değişken tipini tahmin et ve benzersiz yap
            var_prefix = "variable"
            if "gün" in name.lower() or "saat" in name.lower() or "pazar" in values[0].lower():
                var_prefix = "match_info"
            elif "takım" in name.lower() or "vs" in values[0].lower() or "beşiktaş" in values[0].lower() or " - " in name:
                var_prefix = "team_names"
            elif "futbolcu" in name.lower() or "player" in name.lower():
                var_prefix = "player"
            elif "logo" in name.lower():
                var_prefix = "team_logo"
            
            # Benzersiz anahtar oluştur (örn: team_logo_1, player_2)
            var_count = 1
            var_key = f"{var_prefix}_{var_count}"
            while var_key in master_prompt["variables"]:
                var_count += 1
                var_key = f"{var_prefix}_{var_count}"
                
            master_prompt["variables"][var_key] = layer_meta
        else:
            master_prompt["constants"].append(layer_meta)
            
    return master_prompt

if __name__ == "__main__":
    PROMPTS_DIR = "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/prompts/ziraat"
    json_files = [f for f in Path(PROMPTS_DIR).glob("1200x628_*.json") if "master" not in f.name]
    json_files.sort()
    
    if json_files:
        master = compare_psds(json_files)
        output_path = Path(PROMPTS_DIR) / "1200x628_master.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(master, f, ensure_ascii=False, indent=4)
        print(f"Master Prompt Oluşturuldu: {output_path}")
