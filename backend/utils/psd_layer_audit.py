from psd_tools import PSDImage
from pathlib import Path

def audit_psd(psd_path):
    print(f"\nAUDIT: {psd_path}")
    psd = PSDImage.open(psd_path)
    
    def walk_layers(layers, indent=""):
        for l in layers:
            print(f"{indent}{l.name} [{l.kind}] visible={l.visible} opacity={l.opacity}")
            if l.is_group():
                walk_layers(l, indent + "  ")
                
    walk_layers(psd)

if __name__ == "__main__":
    SAMPLES = [
        "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/ziraat/1200x628_png/1.psd",
        "/Users/ayseguler/Documents/vs_projeler/Karbonat/kick-grok/psd_samples/ziraat/1200x628_png/2.psd"
    ]
    for s in SAMPLES:
        audit_psd(s)
