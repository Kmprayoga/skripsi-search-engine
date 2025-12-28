import sqlite3
from collections import defaultdict
import json
from pathlib import Path

DB_PATH = Path("data/skripsi.db")
OUTPUT_PATH = Path("data/processed/index.json")

def build_index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, clean_text FROM skripsi")

    index = defaultdict(lambda: defaultdict(int))
    doc_len = {}

    for doc_id, clean_text in cursor.fetchall():
        tokens = clean_text.split()
        doc_len[str(doc_id)] = len(tokens)

        for token in tokens:
            index[token][str(doc_id)] += 1

    conn.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "index": index,
            "doc_len": doc_len,
            "num_docs": len(doc_len)
        }, f, indent=2)

    print("[OK] Inverted index built from SQLite")

if __name__ == "__main__":
    build_index()
