import pandas as pd
import re
import json
from pathlib import Path

RAW_DATA_PATH = "data/raw/skripsi.csv"
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "corpus.json"

COLUMNS_USED = [
    "Title",
    "Authors",
    "Advisors",
    "Keywords",
    "Abstract",
    "BAB 1",
    "BAB 2",
    "BAB 3",
    "BAB 4",
    "BAB 5",
]

def basic_preprocess(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return text.strip()

def main():
    df = pd.read_csv(RAW_DATA_PATH)

    corpus = []

    for idx, row in df.iterrows():
        parts = []

        for col in COLUMNS_USED:
            if col in df.columns and pd.notna(row[col]):
                parts.append(str(row[col]))

        raw_text = " ".join(parts).strip()
        clean_text = basic_preprocess(raw_text)

        # skip dokumen kosong
        if not clean_text:
            continue

        corpus.append({
            "doc_id": f"doc_{idx}",
            "raw_text": raw_text,
            "clean_text": clean_text
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    print(f"[OK] Corpus built: {len(corpus)} documents")
    print(f"[OK] Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
