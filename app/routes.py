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

routes = Blueprint("routes", __name__)

@routes.route("/search", methods=["GET"])
def search_api():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "query kosong"}), 400

    start = time.perf_counter()
    clean_q = preprocess(q)
    results = bm25_search(clean_q)

    db = get_db()
    cur = db.cursor()

    docs = []
    for doc_id, score in results:
        cur.execute("""
            SELECT title, authors, publisher, pdf_link
            FROM skripsi WHERE id=?
        """, (doc_id,))
        row = cur.fetchone()
        if row:
            docs.append({
                "doc_id": doc_id,
                "title": row["title"],
                "authors": row["authors"],
                "publisher": row["publisher"],
                "pdf": row["pdf_link"],
                "score": score
            })

    elapsed = (time.perf_counter() - start) * 1000
    db.close()

    return jsonify({
        "query": q,
        "time_ms": round(elapsed, 2),
        "results": docs
    })

@routes.route("/upload", methods=["POST"])
def upload_skripsi():
    file = request.files.get("pdf")
    if not file:
        return jsonify({"error": "PDF wajib"}), 400

    filename = f"{uuid.uuid4()}.pdf"
    pdf_path = UPLOAD_DIR / filename
    file.save(pdf_path)

    text = extract_pdf_text(str(pdf_path))
    clean_text = preprocess(text)

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO skripsi (title, authors, publisher, pdf_link, clean_text)
        VALUES (?, ?, ?, ?, ?)
    """, (
        request.form.get("title"),
        request.form.get("authors"),
        request.form.get("publisher"),
        str(pdf_path),
        clean_text
    ))

    db.commit()
    db.close()

    rebuild_indexes()

    return jsonify({"status": "uploaded & indexed"})
