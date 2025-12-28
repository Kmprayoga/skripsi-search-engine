import sqlite3
import time
from pathlib import Path
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from bm25 import bm25_search

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data/skripsi.db"

factory = StemmerFactory()
stemmer = factory.create_stemmer()

def preprocess_query(text: str) -> str:
    text = text.lower()
    return stemmer.stem(text)

def fetch_documents(doc_ids):
    if not doc_ids:
        return []

    placeholders = ",".join("?" for _ in doc_ids)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT id, title, authors, publisher, pdf_link
        FROM skripsi
        WHERE id IN ({placeholders})
    """, doc_ids)

    rows = cursor.fetchall()
    conn.close()

    doc_map = {str(row[0]): row for row in rows}
    ordered = [doc_map[d] for d in map(str, doc_ids) if d in doc_map]

    return ordered

if __name__ == "__main__":
    print("=" * 60)
    query = input("Masukkan query pencarian: ").strip()

    if not query:
        print("Query kosong.")
        exit()

    start_time = time.perf_counter()

    clean_query = preprocess_query(query)

    results = bm25_search(clean_query, top_k=10)
    doc_ids = [doc_id for doc_id, _ in results]

    docs = fetch_documents(doc_ids)

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000

    print("\nHASIL PENCARIAN:")
    print("=" * 60)

    if not docs:
        print("Tidak ada dokumen ditemukan.")
        print(f"\nWaktu pencarian: {elapsed_ms:.2f} ms")
        exit()

    for i, d in enumerate(docs, start=1):
        doc_id, title, authors, publisher, pdf = d
        print(f"\n[{i}] {title}")
        print(f"    Author    : {authors}")
        print(f"    Publisher : {publisher}")
        print(f"    PDF       : {pdf}")

    print("\n" + "=" * 60)
    print(f"Waktu pencarian: {elapsed_ms:.2f} ms")
