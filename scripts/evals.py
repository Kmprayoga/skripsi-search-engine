import json
from app.search import bm25_search
from app.preprocessing import preprocess

QRELS_PATH = "data/evaluation/qrels.json"
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

    total_precision = 0
    total_recall = 0

    for query, relevant_docs in qrels.items():
        processed_query = preprocess(query)
        results = bm25_search(processed_query, top_k=TOP_K)

        retrieved_docs = [doc_id for doc_id, _ in results]

        p, r = precision_recall(retrieved_docs, relevant_docs)

        total_precision += p
        total_recall += r

        print(f"Query: {query}")
        print(f"  Precision@{TOP_K}: {p:.3f}")
        print(f"  Recall@{TOP_K}: {r:.3f}")
        print("-" * 40)

    n = len(qrels)
    print("=== RATA-RATA ===")
    print(f"Mean Precision: {total_precision / n:.3f}")
    print(f"Mean Recall   : {total_recall / n:.3f}")


if __name__ == "__main__":
    evaluate()
