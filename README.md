# Local RAG App with Streamlit, LlamaIndex, ChromaDB, and Ollama

A local retrieval-augmented generation app that lets you upload documents, index them with ChromaDB, and query their content using Ollama's `qwen2.5:3b` model.

## What it does

- Upload supported documents directly through the Streamlit UI
- Persist a Chroma vector store locally in `db/chroma_db`
- Create embeddings with `BAAI/bge-small-en-v1.5`
- Build and reuse a LlamaIndex vector store
- Query indexed documents and receive natural language answers from Ollama

## Requirements

Install Python dependencies:

```bash
pip install -r requirement.txt
```

Also make sure:

- `Ollama` is installed locally
- `Ollama` is running and accessible on your machine

## Supported file formats

- `.pdf`
- `.txt`
- `.md`
- `.json`
- `.yaml`, `.yml`
- `.csv`

## Run the app

From the project root:

```bash
streamlit run app.py
```

Then open the Streamlit URL shown in your browser.

## How to use

1. Upload a document using the file uploader.
2. Click **Load Document** to process and index the file.
3. Enter a question in the text input.
4. See the generated answer and response time.

## Implementation details

- `app.py` contains the full Streamlit UI and application flow
- Uses `llama_index` for document loading, embedding, and querying
- Uses `chromadb` for persistent vector storage
- Uses `llama_index.llms.ollama.Ollama` to call the `qwen2.5:3b` model
- Uses `BAAI/bge-small-en-v1.5` for embeddings

## Persistence

The Chroma database is stored under:

- `db/chroma_db`

If a previous index exists, the app will automatically attempt to load it so you can continue querying without re-uploading files.

## Notes

- The query engine returns the top 3 most similar chunks by default.
- If no index is loaded, you must upload a document first.
- Any errors are shown in the Streamlit UI.

## Dependencies

Current dependencies are listed in `requirement.txt` and include:

- `streamlit`
- `ollama`
- `langchain`
- `langchain-community`
- `chromadb`
- `pypdf`
- `sentence-transformers`
- `pyyaml`

## License

Choose a license and add it here.
