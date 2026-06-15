# Agentic RAG (Ollama + Qwen 2.5)

Upload documents (PDF/TXT/MD/CSV/JSON/YAML), ask questions, and get answers grounded in your uploaded content. The system can also use web search when your question requires up-to-date or public information.

## What’s inside

### Agentic routing
A **Supervisor Agent** decides which route to use:
- **RAG**: use uploaded documents only
- **WEB**: use public internet info only
- **COMPARE**: run both RAG + WEB and synthesize a single answer
- **CHITCHAT**: greetings/casual chat without retrieval

See: `flow-diagram.md`

### Hybrid retrieval (for RAG)
The RAG pipeline uses a hybrid retrieval approach:
- vector similarity search (Chroma)
- keyword retrieval (BM25)
- reciprocal rank fusion
- reranking for better context selection

See: `hybrid-flow.md`

### Logging & traceability
The backend logs selected routes, steps, and sources.

Logs: `backend/logs/rag.log` (and via the `/logs` API)

## Prerequisites

- Python 3.10+ (recommended)
- Node.js + npm (only if you use the React frontend)
- Ollama installed + the model pulled:
  - `qwen2.5:3b`

## Local setup

### 1) Backend (FastAPI)

The backend lives in `backend/app/`.

#### Install dependencies
```bash
cd backend/app
pip install -r requirement.txt
```

#### Start the API server
```bash
cd backend/app
python -m app.main
```

The API docs will be available at:
- `http://127.0.0.1:8000/docs`

Health check:
- `http://127.0.0.1:8000/health`

### 2) Start the Streamlit UI (optional)

The Streamlit app uses the same RAG logic.

#### Run
```bash
streamlit run app.py
```

Then open the printed localhost URL in your browser.

## Endpoints (FastAPI)

- **Chat**: `POST /chat/message`
  - Body includes: `query`, `chat_history` (list of `{role, content}`)
  - Response includes: `answer`, `sources`, and reasoning trace

- **Documents**:
  - `POST /documents/upload` (multipart upload)
  - `GET /documents/list`
  - `GET /documents/{doc_id}`
  - `DELETE /documents/{doc_id}`

- **Logs**:
  - `GET /logs`
  - `GET /logs/stream`

## Usage

1. Upload a document via the UI or `/documents/upload`.
2. Ask a question:
   - If the question matches the documents → the system uses **RAG**.
   - If the question needs up-to-date public info → it uses **WEB**.
   - If it needs both → it uses **COMPARE**.

## Configuration notes

- The core LLM is configured in `backend/app/core/agentic_rag.py` and uses:
  - `model="qwen2.5:3b"`
  - `temperature=0`

If you want to change the model, update the Ollama model name in:
- `backend/app/core/agentic_rag.py`
- `backend/app/agents/rag_agent.py`
- `backend/app/agents/web_agent.py`
- `backend/app/agents/comparison_agent.py`

## Project structure

- `backend/app/core/agentic_rag.py` — supervisor + route execution
- `backend/app/agents/` — RAG agent, Web agent, Comparison agent, tools
- `backend/app/utils/` — indexing/retrieval helpers, query rewriting, memory, logging
- `backend/app/routes/` — FastAPI routes (chat, documents, logs)
- `backend/app/database/` — Chroma DB wrapper

## Problem & solutions

See `Problem-Solved.md` for the problem which is solved by this Agentic-RAG

