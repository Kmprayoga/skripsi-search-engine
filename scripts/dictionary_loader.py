# scripts/dictionary_loader.py
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "data/processed/index.json"

def load_dictionary():
    with open(INDEX_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return set(data["index"].keys())
