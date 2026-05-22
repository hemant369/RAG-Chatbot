import streamlit as st
import time

from src.loader import load_document
from src.splitter import split_text
from src.embeddings import get_embeddings_models
from src.vectorstore import create_or_load_vectorstore
from src.retriever import retrieve_documents
from src.prompt import build_prompt
from src.llm import generate_response

st.title("Document Search with Ollama Qwen 2.5")

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# --- File uploader (multi-format) ---
uploaded_file = st.file_uploader(
    "Upload a document",
    type=["pdf", "txt", "md", "json", "yaml", "yml", "csv"],
)

if uploaded_file and st.button("Load Document"):
    with st.spinner("Processing document..."):
        try:
            text = load_document(uploaded_file)

            if not text.strip():
                st.error("The document appears to be empty or unreadable.")
            else:
                chunks = split_text(text)
                embeddings_model = get_embeddings_models()
                st.session_state.vectorstore = create_or_load_vectorstore(
                    chunks, embeddings_model
                )
                st.success(
                    f"✅ Loaded **{uploaded_file.name}** — "
                    f"{len(chunks)} chunks indexed."
                )
        except ValueError as e:
            st.error(str(e))

# --- Query ---
user_query = st.text_input("Enter your search query:")

if user_query:
    if st.session_state.vectorstore is None:
        st.error("Please load a document first!")
    else:
        start_time = time.time()

        documents = retrieve_documents(st.session_state.vectorstore, user_query)
        final_prompt = build_prompt(documents, user_query)
        answer = generate_response(final_prompt)

        response_time = round(time.time() - start_time, 2)

        st.write(f"**Answer:** {answer}")
        st.write(f"**Response Time:** {response_time} seconds")
