# Ollama Qwen 2.5 Document Search

A local document search application built with Streamlit, Ollama, LangChain, and Chroma.

This app lets you upload documents, build a local semantic index, and ask questions against the content using the Qwen 2.5 model.

## Features

- Upload documents in `pdf`, `txt`, `md`, `json`, `yaml`, `yml`, and `csv` formats
- Convert documents to plain text and split them into semantic chunks
- Embed text chunks using `BAAI/bge-small-en-v1.5`
- Store embeddings in a persistent Chroma vector store
- Retrieve relevant chunks with semantic search
- Generate answers via Ollama using the `qwen2.5:3b` model

## Requirements

Install the Python dependencies:

```bash
pip install -r requirement.txt
```

Also ensure `Ollama` is installed and running locally.

## Setup

1. Open the project root in your terminal.
2. Run the Streamlit app:

```bash
streamlit run app.py
```

3. Open the browser link shown by Streamlit.

## Usage

1. Upload a supported document with the file uploader.
2. Click `Load Document` to process and index the file.
3. Enter a search query in the text input.
4. View the generated answer and the response time.

## Supported File Types

- PDF: `.pdf`
- Text / Markdown: `.txt`, `.md`
- JSON: `.json`
- YAML: `.yaml`, `.yml`
- CSV: `.csv`

## Project Structure

- `app.py` - Streamlit user interface and app flow
- `requirement.txt` - Python dependency list
- `src/embeddings.py` - loads the HuggingFace embedding model
- `src/llm.py` - sends prompts to Ollama and returns the response
- `src/loader.py` - reads uploaded files and converts them to text
- `src/prompt.py` - builds the prompt used by the language model
- `src/retriever.py` - retrieves top-k documents from Chroma
- `src/splitter.py` - splits long text into manageable chunks
- `src/vectorstore.py` - creates or loads the Chroma vector store

## Notes

- The Chroma database is persisted in `db/chroma_db`.
- Queries require a document to be loaded first.
- The app currently returns the top 3 most similar chunks for each query.

## Troubleshooting

- If the uploaded file is unreadable, verify that the file type is supported.
- Ensure `Ollama` is running and accessible.
- If no response appears, check the terminal for error messages.

## License

Add a license of your choice here.
