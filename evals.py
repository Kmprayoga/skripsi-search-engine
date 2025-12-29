import sys
from pathlib import Path
import json

# =========================
# ROOT PROJECT
# =========================
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# =========================
# IMPORT DARI app/
# =========================
from app.search import bm25_search
from app.preprocessing import preprocess

QRELS_PATH = BASE_DIR / "app" / "data" / "evaluation" / "qrels.json"
TOP_K = 10


def precision_recall(retrieved, relevant):
    retrieved = set(retrieved)
    relevant = set(relevant)

    tp = len(retrieved & relevant)
    precision = tp / len(retrieved) if retrieved else 0
    recall = tp / len(relevant) if relevant else 0

    return precision, recall


def evaluate():
    with open(QRELS_PATH) as f:
        qrels = json.load(f)

    total_p = 0
    total_r = 0

    print("=" * 60)

    for query, relevant_docs in qrels.items():
        processed_query = preprocess(query)
        results = bm25_search(processed_query, top_k=TOP_K)

        retrieved_docs = [int(doc_id) for doc_id, _ in results]

        p, r = precision_recall(retrieved_docs, relevant_docs)

        total_p += p
        total_r += r

        print(f"Query: {query}")
        print(f"  Precision@{TOP_K}: {p:.3f}")
        print(f"  Recall@{TOP_K}: {r:.3f}")
        print("-" * 60)

    n = len(qrels)

    print("=== RATA-RATA ===")
    print(f"Mean Precision@{TOP_K}: {total_p / n:.3f}")
    print(f"Mean Recall@{TOP_K}   : {total_r / n:.3f}")
    print("=" * 60)
    print("Retrieved docs:", retrieved_docs)
    print("Relevant docs :", relevant_docs)


if __name__ == "__main__":
    evaluate()
