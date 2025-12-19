from pathlib import Path
import json
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent

CORPUS_PATH = BASE_DIR / "data/processed/corpus.json"
OUTPUT_PATH = BASE_DIR / "data/processed/index.json"


def build_index(corpus):
    index = defaultdict(lambda: defaultdict(int))
    doc_len = {}

    for doc in corpus:
        doc_id = doc["doc_id"]
        tokens = doc["clean_text"].split()
        doc_len[doc_id] = len(tokens)

        for token in tokens:
            index[token][doc_id] += 1

    return index, doc_len

if __name__ == "__main__":
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    index, doc_len = build_index(corpus)

    output = {
        "index": index,
        "doc_len": doc_len,
        "num_docs": len(doc_len)
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("[OK] Inverted index built")
