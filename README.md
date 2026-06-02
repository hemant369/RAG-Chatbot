# Advanced Local RAG App

A local retrieval-augmented generation (RAG) demo built with Streamlit, Ollama, LlamaIndex, and ChromaDB.

## Overview

This repository implements a simple local RAG application that lets you:
- Upload documents in `pdf`, `txt`, `md`, `csv`, `json`, `yaml`, and `yml` formats
- Persist embeddings in a ChromaDB vector store
- Query the indexed documents with a Qwen 2.5 model running locally via Ollama
- Display generated answers alongside retrieved source chunks and metadata

## Features

- Multi-file upload and indexing
- Duplicate prevention using file content hashing
- Persistent ChromaDB storage under `db/chroma_db`
- Hybrid retrieval with vector similarity and BM25
- Sentence transformer reranking for top results
- Streamlit UI with configurable `top_k` similarity search

## Requirements

Install Python dependencies from `requirement.txt`:

```bash
pip install -r requirement.txt
```

You also need a local Ollama instance with access to the `qwen2.5:3b` model.

## Setup

1. Install Ollama and make sure it is running locally.
2. From the project root, run:

```bash
streamlit run app.py
```

3. Open the browser URL shown by Streamlit.

## Usage

1. Upload one or more supported documents using the Streamlit uploader.
2. Click `Load Document` to index the files into ChromaDB.
3. Enter a query in the text input.
4. View the generated answer, source chunks, and metadata.

## Project Structure

- `app.py` - Streamlit application entry point
- `requirement.txt` - Python dependency list
- `database/chroma_db.py` - Persistent ChromaDB client, collection, and vector store setup
- `models/`
  - `embedding_model.py` - HuggingFace embedding model `BAAI/bge-small-en-v1.5`
  - `llm.py` - Ollama LLM client configured for `qwen2.5:3b`
  - `reranker.py` - SentenceTransformer reranker `BAAI/bge-reranker-base`
- `utils/`
  - `document_loader.py` - Loads uploaded files into LlamaIndex documents
  - `document_manager.py` - Generates file hashes and checks for duplicates
  - `query_engine.py` - Builds the retrieval and query engine using hybrid search

## Supported File Types

- `pdf`
- `txt`
- `md`
- `csv`
- `json`
- `yaml`
- `yml`

## Notes

- The vector database is persisted in `db/chroma_db`.
- Duplicate files are detected by hashing uploaded file bytes.
- Querying combines a Chroma vector retriever, BM25 retriever, and `qwen2.5:3b`.

## License

Add a license or choose one that fits your project requirements.
