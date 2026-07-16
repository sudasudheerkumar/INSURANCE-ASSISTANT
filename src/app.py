"""
app.py
Interactive command-line chat loop for asking questions about your
insurance documents. Run ingest.py and embed.py first.

Usage:
    python src/app.py
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from query import ask_claude, build_context, retrieve  # noqa: E402

load_dotenv()

DB_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "insurance_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def main():
    if not DB_DIR.exists():
        print("No chroma_db found. Run these first:")
        print("  python src/ingest.py")
        print("  python src/embed.py")
        return

    print("Loading model and index ...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_collection(COLLECTION_NAME)

    print("\nInsurance Document Assistant")
    print("Ask a question, or type 'exit' to quit.\n")

    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        chunks = retrieve(question, model, collection)
        context = build_context(chunks)
        answer = ask_claude(question, context)

        print(f"\n{answer}\n")
        print("Sources: " + ", ".join(f"{c['source']} p{c['page']}" for c in chunks))
        print()


if __name__ == "__main__":
    main()
