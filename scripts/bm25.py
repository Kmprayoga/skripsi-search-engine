import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "data/processed/index.json"

K1 = 1.5
B = 0.75


with open(INDEX_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

INDEX = DATA["index"]
DOC_LEN = DATA["doc_len"]
N = DATA["num_docs"]
AVGDL = sum(DOC_LEN.values()) / N


def bm25_search(query, top_k=10):
    scores = {}
    terms = query.split()

    for term in terms:
        if term not in INDEX:
            continue

        postings = INDEX[term]
        df = len(postings)

        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

        for doc_id, tf in postings.items():
            dl = DOC_LEN[doc_id]
            denom = tf + K1 * (1 - B + B * dl / AVGDL)
            score = idf * ((tf * (K1 + 1)) / denom)
            scores[doc_id] = scores.get(doc_id, 0) + score

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
