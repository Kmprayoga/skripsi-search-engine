import json
import math
from app.config import PROCESSED_DIR

INDEX_PATH = PROCESSED_DIR / "index.json"

K1 = 1.5
B = 0.75

with open(INDEX_PATH) as f:
    DATA = json.load(f)

INDEX = DATA["index"]
DOC_LEN = DATA["doc_len"]
N = DATA["num_docs"]
AVGDL = sum(DOC_LEN.values()) / N

def bm25_search(query: str, top_k=10):
    scores = {}

    for term in query.split():
        if term not in INDEX:
            continue

        df = len(INDEX[term])
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

        for doc_id, tf in INDEX[term].items():
            dl = DOC_LEN[doc_id]
            score = idf * ((tf * (K1 + 1)) /
                           (tf + K1 * (1 - B + B * dl / AVGDL)))
            scores[doc_id] = scores.get(doc_id, 0) + score

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
