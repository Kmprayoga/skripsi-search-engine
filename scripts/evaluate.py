from bm25 import bm25_search
from typing import List, Set

# =========================
# Ground Truth (contoh)
# =========================
# Mapping query -> dokumen yang BENAR-BENAR relevan
# doc_id harus SAMA dengan id di database (string / int konsisten)
GROUND_TRUTH = {
    "analisis sentimen": {"3", "7", "10", "1"},
    "machine learning": {"5", "12", "20"},
    "data mining": {"8", "15"},
}


# =========================
# Precision & Recall
# =========================
def precision_recall(
    retrieved: List[str],
    relevant: Set[str]
):
    retrieved_set = set(retrieved)

    if not retrieved_set:
        return 0.0, 0.0

    true_positive = len(retrieved_set & relevant)

    precision = true_positive / len(retrieved_set)
    recall = true_positive / len(relevant) if relevant else 0.0

    return precision, recall


# =========================
# Evaluation Runner
# =========================
def evaluate_query(query: str, top_k: int = 10):
    results = bm25_search(query, top_k)

    # hasil BM25: [(doc_id, score), ...]
    retrieved_ids = [str(doc_id) for doc_id, _ in results]

    relevant_ids = GROUND_TRUTH.get(query, set())

    precision, recall = precision_recall(retrieved_ids, relevant_ids)

    print("=" * 50)
    print(f"Query     : {query}")
    print(f"Retrieved : {retrieved_ids}")
    print(f"Relevant  : {sorted(list(relevant_ids))}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print("=" * 50)


# =========================
# Main
# =========================
if __name__ == "__main__":
    QUERY = "analisis kesiapan dan penerimaan menggunakan technology readiness and acceptance model (tram) pada chatgpt"
    TOP_K = 10

    evaluate_query(QUERY, TOP_K)
