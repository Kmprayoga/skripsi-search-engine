from flask import Flask, request, jsonify
import time
import sqlite3
from pathlib import Path
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from bm25 import bm25_search
from spelling import SpellCorrector
from wildcard import WildcardExpander

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data/skripsi.db"

stemmer = StemmerFactory().create_stemmer()
spell = SpellCorrector()          # kgram.json
wildcard = WildcardExpander()     # permuterm.json

def preprocess_normal(text: str) -> list[str]:
    text = text.lower()
    text = stemmer.stem(text)
    return text.split()

def fetch_documents(doc_ids):
    if not doc_ids:
        return []

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    placeholders = ",".join("?" for _ in doc_ids)
    cur.execute(f"""
        SELECT id, title, authors, publisher, pdf_link
        FROM skripsi
        WHERE id IN ({placeholders})
    """, doc_ids)

    rows = cur.fetchall()
    conn.close()

    doc_map = {str(r[0]): r for r in rows}
    return [doc_map[str(d)] for d in doc_ids if str(d) in doc_map]

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    mode = request.args.get("mode", "normal")  # normal | wildcard

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    start = time.perf_counter()

    corrected_query = query
    final_terms = []

    # ------------------
    # NORMAL SEARCH
    # ------------------
    if mode == "normal":
        tokens = preprocess_normal(query)
        is_corrected = False

        for t in tokens:
            corrected = spell.correct(t)
            if corrected != t:
                is_corrected = True
            final_terms.append(corrected)

        if is_corrected:
            corrected_query = " ".join(final_terms)

    elif mode == "wildcard":
        tokens = query.lower().split()

        for t in tokens:
            if "*" in t:
                expanded = wildcard.expand(t)
                final_terms.extend(expanded)
            else:
                final_terms.append(t)

    else:
        return jsonify({"error": "mode must be 'normal' or 'wildcard'"}), 400

    final_query = " ".join(final_terms)

    # BM25
    results = bm25_search(final_query, top_k=10)
    doc_ids = [doc_id for doc_id, _ in results]
    docs = fetch_documents(doc_ids)

    elapsed = (time.perf_counter() - start) * 1000

    response = {
        "query": query,
        "corrected_query": corrected_query if corrected_query != query else None,
        "final_query": final_query,
        "search_time_ms": round(elapsed, 2),
        "results": []
    }

    for rank, d in enumerate(docs, start=1):
        response["results"].append({
            "rank": rank,
            "title": d[1],
            "authors": d[2],
            "publisher": d[3],
            "pdf": d[4]
        })

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
