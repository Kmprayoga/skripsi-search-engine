# scripts/build_kgram.py
import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "data/processed/index.json"
KGRAM_PATH = BASE_DIR / "data/processed/kgram.json"

K = 3

def build_kgrams(term):
    term = f"${term}$"
    return [term[i:i+K] for i in range(len(term)-K+1)]

with open(INDEX_PATH) as f:
    terms = json.load(f)["index"].keys()

kgram_index = defaultdict(set)

for term in terms:
    for kg in build_kgrams(term):
        kgram_index[kg].add(term)

with open(KGRAM_PATH, "w") as f:
    json.dump({k: list(v) for k, v in kgram_index.items()}, f, indent=2)

print("[OK] K-Gram index built")
