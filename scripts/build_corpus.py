import sqlite3
import json
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

DB_PATH = "db/skripsi.db"
OUTPUT = "data/processed/corpus.json"

stemmer = StemmerFactory().create_stemmer()

def preprocess(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return stemmer.stem(text).strip()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, title, authors, keywords, abstract FROM skripsi")

corpus = []

for row in cursor.fetchall():
    doc_id, title, authors, keywords, abstract = row

    combined = " ".join([
        str(title),
        str(authors),
        str(keywords),
        str(abstract),
    ])

    clean = preprocess(combined)
    if not clean:
        continue

    corpus.append({
        "doc_id": doc_id,
        "text": clean
    })

conn.close()

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(corpus, f, indent=2, ensure_ascii=False)

print(f"[OK] Corpus built: {len(corpus)} docs")
