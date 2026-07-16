"""
query.py
Given a question, retrieves the most relevant chunks from the vector
store and asks Claude to answer using only that retrieved context.

Usage:
    python src/query.py "What does my policy say about uninsured motorists?"
"""

import os
import sys
from pathlib import Path

import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

DB_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "insurance_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5
CLAUDE_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are an assistant answering questions about the user's \
insurance documents. Only use the provided context to answer -- do not use \
outside knowledge. If the context doesn't contain the answer, say so clearly. \
Always mention which source document and page number your answer is based on."""


def retrieve(question: str, model: SentenceTransformer, collection) -> list[dict]:
    query_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=TOP_K)

    retrieved = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        retrieved.append({"text": doc, "source": meta["source"], "page": meta["page"]})
    return retrieved


def build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(f"[Source: {c['source']}, page {c['page']}]\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def ask_claude(question: str, context: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
        )

    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            }
        ],
    )
    return message.content[0].text


def main():
    if len(sys.argv) < 2:
        print('Usage: python src/query.py "your question here"')
        return

    question = " ".join(sys.argv[1:])

    if not DB_DIR.exists():
        print("No chroma_db found. Run 'python src/embed.py' first.")
        return

    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_collection(COLLECTION_NAME)

    chunks = retrieve(question, model, collection)
    context = build_context(chunks)

    print("\n--- Answer ---\n")
    answer = ask_claude(question, context)
    print(answer)

    print("\n--- Retrieved from ---")
    for c in chunks:
        print(f"  {c['source']} (page {c['page']})")


if __name__ == "__main__":
    main()
