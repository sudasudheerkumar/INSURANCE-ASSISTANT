"""
ingest.py
Extracts text from PDFs in data/raw/ and splits it into chunks
saved as JSON in data/processed/chunks.json.

Usage:
    python src/ingest.py
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
CHUNKS_FILE = PROCESSED_DIR / "chunks.json"

# Roughly how many characters per chunk. Insurance text is dense,
# so smaller chunks tend to retrieve more precisely than huge ones.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def extract_text_by_page(pdf_path: Path) -> list[str]:
    """Return a list of raw text strings, one per page."""
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return pages


def clean_text(text: str) -> str:
    """Collapse excess whitespace/line breaks from PDF extraction."""
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Simple sliding-window chunker over cleaned text."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def process_pdf(pdf_path: Path) -> list[dict]:
    """Extract, clean, and chunk a single PDF. Returns chunk records."""
    pages = extract_text_by_page(pdf_path)
    records = []
    for page_num, raw_page in enumerate(pages, start=1):
        cleaned = clean_text(raw_page)
        if not cleaned:
            continue
        for i, chunk in enumerate(chunk_text(cleaned, CHUNK_SIZE, CHUNK_OVERLAP)):
            records.append(
                {
                    "id": f"{pdf_path.stem}_p{page_num}_c{i}",
                    "source": pdf_path.name,
                    "page": page_num,
                    "text": chunk,
                }
            )
    return records


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {RAW_DIR}. Add your PDFs there and re-run.")
        return

    all_chunks = []
    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name} ...")
        chunks = process_pdf(pdf_path)
        print(f"  -> {len(chunks)} chunks")
        all_chunks.extend(chunks)

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"\nDone. {len(all_chunks)} total chunks written to {CHUNKS_FILE}")


if __name__ == "__main__":
    main()
