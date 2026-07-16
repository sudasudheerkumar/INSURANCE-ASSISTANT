# Insurance Document Assistant

A local RAG (Retrieval-Augmented Generation) tool that lets you ask natural
language questions about your insurance PDFs (handbooks, policies, etc.) and
get answers grounded in the actual document text, with source citations.

## What This Pipeline Does

The pipeline follows this flow:

1. Load source documents.
2. Clean and split documents into smaller chunks.
3. Convert chunks into embeddings.
4. Store embeddings in a vector database.
5. Retrieve relevant chunks for a user question.
6. Send the question plus retrieved context to an LLM.
7. Return a grounded answer with optional source references

```text
Documents
   |
   v
Load -> Clean -> Chunk -> Embed -> Store in Vector DB
                                      |
User Question                         |
   |                                  v
   +-------------> Retrieve Relevant Context
                                      |
                                      v
                          Prompt LLM with Context
                                      |
                                      v
                              Final Answer
```

## Setup

1. create folder as insurence-assistant  in VS Code.

2. Create a virtual environment and install dependencies:
   ```bash
  
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1


   ```powershell
  pip install -r requirements.txt
   ```

3. Add your Anthropic API key:
   ```bash
   cp .env.example .env
   # then edit .env and paste in your key
   ```

4. Drop your PDFs into `data/raw/`.

## Usage

Run these once (or whenever you add new PDFs):

```bash
python src/ingest.py   # extract + chunk text
python src/embed.py    # build the vector index
```

Then ask questions either as a one-off command:

```bash
python src/query.py "What does collision coverage pay for?"
```

or in an interactive chat loop:

```bash
python src/app.py
```

## Project structure

```
insurance-assistant/
├── data/
│   ├── raw/              # put your PDFs here
│   └── processed/        # extracted/chunked text (auto-generated)
├── src/
│   ├── ingest.py         # PDF -> text -> chunks
│   ├── embed.py          # chunks -> vector index
│   ├── query.py          # retrieval + answer generation
│   └── app.py            # interactive CLI
├── requirements.txt
├── .env
└── README.md
```

