import sys
from psd_tools import PSDImage
import os

def list_all_layers(psd_path):
    print(f"Analyzing: {psd_path}")
    psd = PSDImage.open(psd_path)
    
    for layer in psd.descendants():
        print(f"Layer: '{layer.name}' (Kind: {layer.kind})")
        print(f"  Coords: (Top: {layer.top}, Left: {layer.left}, Width: {layer.width}, Height: {layer.height})")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        psd_path = sys.argv[1]
    else:
        psd_path = "/Users/ayseguler/Documents/vs_projeler/Karbonat/karbonat_docs/proof_of_work/turkiye-ziraat_uefa-conference/turkiye-ziraat/1200x628.psd"
    list_all_layers(psd_path)
