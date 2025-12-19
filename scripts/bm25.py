import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "data/processed/index.json"

K1 = 1.5
B = 0.75

def bm25_score(query, index, doc_len):
    scores = {}
    N = len(doc_len)
    avgdl = sum(doc_len.values()) / N

    for term in query.split():
        if term not in index:
            continue

        df = len(index[term])
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

        for doc_id, tf in index[term].items():
            dl = doc_len[doc_id]
            score = idf * ((tf * (K1 + 1)) / (tf + K1 * (1 - B + B * dl / avgdl)))
            scores[doc_id] = scores.get(doc_id, 0) + score

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

if __name__ == "__main__":
    with open(INDEX_PATH) as f:
        data = json.load(f)

    query = input("Query: ").lower()
    results = bm25_score(query, data["index"], data["doc_len"])

    for doc_id, score in results[:10]:
        print(doc_id, score)
