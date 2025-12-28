from flask import Blueprint, request, jsonify
from pathlib import Path
import uuid
import time

from app.database import get_db
from app.preprocessing import preprocess
from app.pdf_extractor import extract_pdf_text
from app.indexer import rebuild_indexes
from app.search import bm25_search
from app.config import UPLOAD_DIR

from scripts.spelling import SpellCorrector
from scripts.wildcard import WildcardExpander

routes = Blueprint("routes", __name__)

spell_corrector = SpellCorrector(k=3, max_dist=2)
wildcard_expander = WildcardExpander()

@routes.route("/search", methods=["POST"])
def search_api():
    data = request.get_json(silent=True)

    if not data or "query" not in data:
        return jsonify({"error": "field 'query' wajib diisi"}), 400

    original_query = data["query"].strip()
    if not original_query:
        return jsonify({"error": "query kosong"}), 400

    start = time.perf_counter()

    expanded_terms = []
    for term in original_query.split():
        expanded_terms.extend(wildcard_expander.expand(term))

    wildcard_query = " ".join(expanded_terms)

    corrected_terms = [
        spell_corrector.correct(term) for term in expanded_terms
    ]
    corrected_query = " ".join(corrected_terms)

    final_query = preprocess(corrected_query)

    results = bm25_search(final_query)

    db = get_db()
    cur = db.cursor()

    docs = []
    for doc_id, score in results:
        cur.execute("""
            SELECT title, authors, publisher, pdf_link
            FROM skripsi
            WHERE id = ?
        """, (doc_id,))
        row = cur.fetchone()

        if row:
            docs.append({
                "doc_id": doc_id,
                "title": row["title"],
                "authors": row["authors"],
                "publisher": row["publisher"],
                "pdf_link": row["pdf_link"],
                "score": round(score, 4)
            })

    db.close()

    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return jsonify({
        "original_query": original_query,
        "wildcard_query": wildcard_query,
        "corrected_query": corrected_query,
        "final_query": final_query,
        "time_ms": elapsed,
        "total_results": len(docs),
        "results": docs
    })

@routes.route("/upload", methods=["POST"])
def upload_skripsi():
    file = request.files.get("pdf")
    if not file:
        return jsonify({"error": "file PDF wajib"}), 400

    title = request.form.get("title")
    authors = request.form.get("authors")
    publisher = request.form.get("publisher", "")

    if not title or not authors:
        return jsonify({"error": "title dan authors wajib"}), 400

    filename = f"{uuid.uuid4().hex}.pdf"
    pdf_path = UPLOAD_DIR / filename
    file.save(pdf_path)

    raw_text = extract_pdf_text(str(pdf_path))
    clean_text = preprocess(raw_text)

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO skripsi (title, authors, publisher, pdf_link, clean_text)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        authors,
        publisher,
        str(pdf_path),
        clean_text
    ))

    db.commit()
    db.close()

    # rebuild index
    rebuild_indexes()

    return jsonify({
        "status": "uploaded & indexed",
        "file": filename
    }), 201
