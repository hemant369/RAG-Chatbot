import streamlit as st
import tempfile
import time
import os

import chromadb

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


st.set_page_config(page_title="Local RAG App", layout="wide")

st.title("📄 Local RAG App with LlamaIndex + ChromaDB + Ollama")


if "query_engine" not in st.session_state:
    st.session_state.query_engine = None

# -----------------------------
# CHROMA DB SETUP
# -----------------------------

# Persistent database folder
db = chromadb.PersistentClient(path="db/chroma_db")

# Create or load collection
chroma_collection = db.get_or_create_collection("documents")

# Create vector store
vector_store = ChromaVectorStore(
    chroma_collection=chroma_collection
)

# Storage context
storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


llm = Ollama(
    model="qwen2.5:3b",
    request_timeout=120.0
)


uploaded_file = st.file_uploader(
    "Upload a document",
    type=["pdf", "txt", "md", "json", "yaml", "yml", "csv"],
)

if uploaded_file and st.button("Load Document"):

    with st.spinner("Processing and indexing document..."):

        try:

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(uploaded_file.name)[1]
            ) as tmp_file:

                tmp_file.write(uploaded_file.read())
                temp_path = tmp_file.name

            # Load document
            documents = SimpleDirectoryReader(
                input_files=[temp_path]
            ).load_data()

            # Create index
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                embed_model=embed_model,
            )

            # Create query engine
            query_engine = index.as_query_engine(
                llm=llm,
                similarity_top_k=3,
            )

            # Save in session state
            st.session_state.query_engine = query_engine

            st.success(
                f"✅ {uploaded_file.name} indexed successfully!"
            )

        except Exception as e:
            st.error(f"Error: {str(e)}")


if st.session_state.query_engine is None:

    try:

        # Load existing index from Chroma
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embed_model,
        )

        # Create query engine
        st.session_state.query_engine = index.as_query_engine(
            llm=llm,
            similarity_top_k=3,
        )

    except:
        pass


query = st.text_input("Ask a question about your documents")

if query:

    if st.session_state.query_engine is None:

        st.error("Please upload and index a document first!")

    else:

        with st.spinner("Generating response..."):

            try:

                start_time = time.time()

                # Query the RAG pipeline
                response = st.session_state.query_engine.query(query)

                response_time = round(
                    time.time() - start_time,
                    2
                )

                # Display answer
                st.subheader("Answer")
                st.write(str(response))

                # Response time
                st.caption(
                    f"⏱ Response Time: {response_time} seconds"
                )

            except Exception as e:

                st.error(f"Error: {str(e)}")





