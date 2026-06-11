# Advanced RAG Assistant

A local retrieval-augmented generation (RAG) demo using Streamlit, Ollama, LlamaIndex, and ChromaDB.

## What this project does

This repository provides a local knowledge-base assistant that lets you:
- Upload documents (`pdf`, `txt`, `md`, `csv`, `json`, `yaml`, `yml`)
- Index them into a persistent ChromaDB vector store
- Query the document collection using a local `qwen2.5:3b` Ollama model
- Use a hybrid retrieval pipeline combining vector similarity, BM25, and reranking
- Chat with your document corpus while preserving session history

## Key features

- Streamlit-powered web interface
- Multi-file upload and indexing
- Duplicate detection via file content hashing
- Persistent ChromaDB storage under `db/chroma_db`
- Hybrid retrieval with a vector retriever, BM25 retriever, and reciprocal rerank fusion
- Agent-driven query execution with tools for document search, calculation, and document listing
- Simple chat memory for conversational context

## Requirements

- Python 3.10+
- Ollama installed and running locally
- Local access to the `qwen2.5:3b` model in Ollama

Install Python dependencies:

```bash
pip install -r requirement.txt
```

## Setup

1. Start Ollama locally and ensure the `qwen2.5:3b` model is available.
2. From the project root, run:

```bash
streamlit run app.py
```

3. Open the Streamlit URL shown in the terminal.

## Usage

1. Upload supported documents in the sidebar.
2. Click `Index Documents` to store them in ChromaDB.
3. Enter a query in the chat input at the bottom.
4. Review the assistant response and query details.
5. Use `Clear` or `New Chat` to reset the conversation context.

## Project structure

- `app.py` - Streamlit UI, upload/index actions, chat flow, and session state
- `requirement.txt` - Python dependencies
- `database/chroma_db.py` - ChromaDB persistent client and vector store setup
- `models/`
  - `embedding_model.py` - Embedding model for document vectors
  - `llm.py` - Ollama LLM client configuration
  - `reranker.py` - Sentence transformer reranker for retrieved results
- `utils/`
  - `chat_memory.py` - Chat history management in Streamlit session state
  - `document_loader.py` - Loads uploaded files into document objects
  - `document_manager.py` - Hash-based duplicate detection for uploaded files
  - `query_engine.py` - Builds the hybrid retrieval/query engine
- `agents/`
  - `rag_agent.py` - Agent creation using Ollama and tool integration
  - `tools.py` - Tools for searching indexed documents, performing calculations, and listing files

## Supported file formats

- `pdf`
- `txt`
- `md`
- `csv`
- `json`
- `yaml`
- `yml`

## Notes

- Indexed document chunks are stored in a local ChromaDB persistent store.
- Document uploads are hashed so reruns do not re-index the same file.
- Query execution uses a hybrid retriever, with vector search and BM25 fused by LlamaIndex.
- The application supports conversational context through session-based chat memory.

## License

This repository does not include a license by default. Add one if you want to share or publish the project.
