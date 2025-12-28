import sqlite3
import pandas as pd
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

DB_PATH = "data/skripsi.db"
CSV_PATH = "data/raw/skripsi.csv"

factory = StemmerFactory()
stemmer = factory.create_stemmer()

def preprocess(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return stemmer.stem(text)

def main():
    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        parts = []
        for col in ["Title", "Authors", "Keywords", "Abstract", "BAB 1", "BAB 2", "BAB 3", "BAB 4", "BAB 5"]:
            if col in df.columns and pd.notna(row[col]):
                parts.append(str(row[col]))

        raw_text = " ".join(parts)
        clean_text = preprocess(raw_text)

        cursor.execute("""
            INSERT INTO skripsi
            (title, authors, advisors, publisher, keywords,
             abstract, bab1, bab2, bab3, bab4, bab5, pdf_link, clean_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("Title"),
            row.get("Authors"),
            row.get("Advisors"),
            row.get("Publisher"),
            row.get("Keywords"),
            row.get("Abstract"),
            row.get("BAB 1"),
            row.get("BAB 2"),
            row.get("BAB 3"),
            row.get("BAB 4"),
            row.get("BAB 5"),
            row.get("Link PDF"),
            clean_text
        ))

    conn.commit()
    conn.close()
    print("[OK] Data imported & preprocessed into SQLite")

if __name__ == "__main__":
    main()
