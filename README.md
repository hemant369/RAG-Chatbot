# Advanced Local RAG App

A Streamlit-based local retrieval-augmented generation (RAG) application built with Ollama, LangChain/LlamaIndex, and Chroma for vector persistence.

## Overview

This repository provides a local RAG app that:
- Uploads documents in formats like `pdf`, `txt`, `md`, `csv`, `json`, `yaml`, and `yml`
- Detects a document category automatically (`HR`, `Finance`, `Legal`, or `General`)
- Indexes uploaded documents in a Chroma vector store
- Answers user questions using Qwen 2.5 via Ollama
- Displays retrieved source chunks and metadata

## Features

- Document upload and indexing
- Category detection for documents and queries
- Semantic search with category filtering
- Sentence-transformer reranking of retrieved nodes
- Streamlit UI for easy interaction

## Requirements

Install the Python dependencies from `requirement.txt`:

```bash
pip install -r requirement.txt
```

## Setup

1. Ensure `Ollama` is installed and running locally.
2. Start the Streamlit app from the project root:

```bash
streamlit run app.py
```

3. Open the browser link shown by Streamlit.

## Usage

1. Upload a supported document using the file uploader.
2. Click `Load Document` to index the file and detect its category.
3. Enter a question in the query input.
4. Review the answer, retrieved chunks, and metadata.

## Project Structure

- `app.py` - Streamlit application entry point
- `requirement.txt` - Python dependency list
- `database/chroma_db.py` - Chroma client and persistent vector store setup
- `models/`
  - `embedding_model.py` - HuggingFace embedding model `BAAI/bge-small-en-v1.5`
  - `llm.py` - Ollama LLM client configured for `qwen2.5:3b`
  - `reranker.py` - Sentence transformer reranker `BAAI/bge-reranker-base`
- `utils/`
  - `category_detector.py` - document/query category detection logic
  - `document_loader.py` - document ingestion helpers
  - `query_engine.py` - index creation and query engine setup

## Notes

- The Chroma vector database is persisted under `db/chroma_db`.
- Category detection is keyword-based and currently supports `HR`, `Finance`, `Legal`, and `General`.
- Query routing uses the detected category to filter retrieved documents when available.

## License

Add your preferred license here.
