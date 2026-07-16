
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
CHUNKS_FILE = PROCESSED_DIR / "chunks.json"
DB_DIR = Path(__file__).parent.parent / "chroma_db"

COLLECTION_NAME = "insurance_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small, fast, runs locally (no API key needed)


def main():
    if not CHUNKS_FILE.exists():
        print("No chunks.json found. Run 'python src/ingest.py' first.")
        return

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loading embedding model '{EMBEDDING_MODEL}' ...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Embedding {len(chunks)} chunks ...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=str(DB_DIR))
    # Start fresh each time this script runs
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"source": c["source"], "page": c["page"]} for c in chunks],
    )

    print(f"\nDone. {len(chunks)} chunks embedded and stored in {DB_DIR}")


if __name__ == "__main__":
    main()
