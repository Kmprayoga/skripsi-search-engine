import time
import sqlite3
from pathlib import Path
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from bm25 import bm25_search
from spelling import SpellCorrector          # berbasis kgram.json
from wildcard import WildcardExpander        # berbasis blocks.json + frontcoded.json

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data/skripsi.db"

stemmer = StemmerFactory().create_stemmer()
spell = SpellCorrector()
wildcard = WildcardExpander()

def preprocess_query(text: str) -> list[str]:
    """
    Case folding + stemming + tokenisasi
    """
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

if __name__ == "__main__":
    print("=" * 60)
    query = input("Masukkan query pencarian: ").strip()

    if not query:
        print("Query kosong.")
        exit()

    start_time = time.perf_counter()

    tokens = preprocess_query(query)

    final_terms = []
    corrected_terms = []
    is_corrected = False

    for token in tokens:

        if "*" in token:
            expanded_terms = wildcard.expand(token)

            if expanded_terms:
                final_terms.extend(expanded_terms)
            else:
                final_terms.append(token)

            corrected_terms.append(token)
            continue

        corrected = spell.correct(token)

        if corrected != token:
            is_corrected = True

        final_terms.append(corrected)
        corrected_terms.append(corrected)

    final_query = " ".join(final_terms)
    corrected_query = " ".join(corrected_terms)

    if is_corrected:
        print(f"\nMaksud Anda: {corrected_query} ?\n")

    results = bm25_search(final_query, top_k=10)
    doc_ids = [doc_id for doc_id, _ in results]

    docs = fetch_documents(doc_ids)

    print("\nHASIL PENCARIAN:")
    print("=" * 60)

    if not docs:
        print("Tidak ada dokumen ditemukan.")
    else:
        for i, d in enumerate(docs, start=1):
            doc_id, title, authors, publisher, pdf = d
            print(f"\n[{i}] {title}")
            print(f"    Author    : {authors}")
            print(f"    Publisher : {publisher}")
            print(f"    PDF       : {pdf}")

    elapsed = (time.perf_counter() - start_time) * 1000
    print("\n" + "=" * 60)
    print(f"Waktu pencarian: {elapsed:.2f} ms")
