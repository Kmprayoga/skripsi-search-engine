import fitz  # PyMuPDF

def extract_pdf_text(pdf_path: str) -> str:
    text = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text.append(page.get_text())
    return " ".join(text)
