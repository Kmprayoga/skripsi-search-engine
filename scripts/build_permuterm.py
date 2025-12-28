# scripts/build_permuterm.py
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "data/processed/index.json"
PERMUTERM_PATH = BASE_DIR / "data/processed/permuterm.json"

def build_permuterm(terms):
    permuterm = defaultdict(list)

    for term in terms:
        t = term + "$"
        for i in range(len(t)):
            rotated = t[i:] + t[:i]
            permuterm[rotated].append(term)

    return permuterm

if __name__ == "__main__":
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)["index"]

    terms = index.keys()
    permuterm = build_permuterm(terms)

    with open(PERMUTERM_PATH, "w", encoding="utf-8") as f:
        json.dump(permuterm, f, indent=2)

    print("[OK] Permuterm index built")
