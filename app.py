import time
import streamlit as st

from backend.app.utils.chat_memory import (
    get_chat_context,
    initialize_memory,
    add_user_message,
    add_assistant_message,
    clear_memory,
)

from backend.app.utils.document_loader import (
    load_uploaded_document,
)

from backend.app.utils.document_manager import (
    generate_file_hash,
    document_exists,
)

from backend.app.utils.query_engine import (
    create_index,
)

from database.chroma_db import (
    chroma_collection,
)

from agents.rag_agent import (
    get_agent,
)

from backend.app.utils.query_rewriter import rewrite_query

from backend.app.utils.logger import logger

UPLOAD_TYPES = [
    "pdf",
    "txt",
    "md",
    "csv",
    "json",
    "yaml",
    "yml",
]


@st.cache_resource
def init_app():
    """Initialize app once per session."""
    initialize_memory()
    logger.info("Streamlit app initialized and chat memory ready")


def set_page_config():
    st.set_page_config(
        page_title="Advanced RAG Assistant",
        page_icon="🤖",
        layout="wide",
    )

    st.markdown(
        """
        <style>

        .block-container {
            max-width: 1100px;
            padding-top: 1rem;
        }

        .stChatMessage {
            border-radius: 12px;
            padding: 10px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.title("🤖 Advanced RAG Assistant")
    st.caption("Upload documents and chat with your knowledge base")


def process_uploaded_files(uploaded_files):
    if not uploaded_files:
        st.warning("Please select one or more files before indexing.")
        return

    logger.info(
        f"Indexing documents button pressed. Uploaded files: {len(uploaded_files)}"
    )

    with st.spinner("Indexing documents..."):
        try:
            for uploaded_file in uploaded_files:
                documents = load_uploaded_document(uploaded_file)
                file_hash = generate_file_hash(uploaded_file)

                if document_exists(file_hash):
                    logger.info(f"Document already indexed: {uploaded_file.name}")
                    st.warning(f"{uploaded_file.name} already indexed.")
                    continue

                for doc in documents:
                    doc.metadata = {
                        "file_name": uploaded_file.name,
                        "file_hash": file_hash,
                    }

                logger.info(f"Creating index for {uploaded_file.name}")
                create_index(documents)
                logger.info(f"Successfully indexed {uploaded_file.name}")
                st.success(f"✅ {uploaded_file.name} indexed")

        except Exception as e:
            logger.exception("Document indexing failed")
            st.error(f"Error: {str(e)}")


def get_indexed_documents():
    try:
        results = chroma_collection.get()
        if len(results["ids"]) == 0:
            return []

        unique_files = set()
        for meta in results.get("metadatas", []):
            if meta and "file_name" in meta:
                unique_files.add(meta["file_name"])

        return sorted(unique_files)

    except Exception:
        logger.exception("Failed to fetch indexed documents")
        return []


def render_sidebar():
    st.header("📚 Knowledge Base")

    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=UPLOAD_TYPES,
        accept_multiple_files=True,
    )

    if st.button("📥 Index Documents"):
        process_uploaded_files(uploaded_files)

    st.divider()

    top_k = st.slider(
        "Similarity Top K",
        min_value=1,
        max_value=20,
        value=10,
    )

    st.divider()

    st.subheader("📄 Indexed Documents")
    indexed_docs = get_indexed_documents()

    if indexed_docs:
        for file_name in indexed_docs:
            st.success(file_name)

        logger.info(
            f"Displayed {len(indexed_docs)} indexed document(s) in sidebar"
        )
    else:
        logger.info("No indexed documents to display in sidebar")
        st.info("No documents indexed.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑 Clear"):
            logger.info("Clear chat button pressed")
            clear_memory()
            st.rerun()

    with col2:
        if st.button("🔄 New Chat"):
            logger.info("New chat button pressed")
            clear_memory()
            st.rerun()

    return top_k


def render_chat_history():
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def handle_query(query):
    with st.chat_message("user"):
        st.markdown(query)

    add_user_message(query)
    logger.info(f"User Query: {query}")

    try:
        start_time = time.time()
        agent = get_agent()
        chat_context = get_chat_context()

        logger.info("Starting query rewrite")
        rewritten_query = rewrite_query(question=query, chat_context=chat_context)
        logger.info(f"Rewritten Query: {rewritten_query}")

        logger.info("Invoking RAG Agent")
        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": rewritten_query,
                    }
                ]
            }
        )

        answer = str(response["messages"][-1].content)
        logger.info(f"Response Length: {len(answer)} characters")

        if not answer.strip():
            answer = "No response generated."

        with st.chat_message("assistant"):
            placeholder = st.empty()
            streamed_text = ""

            for word in answer.split():
                streamed_text += word + " "
                placeholder.markdown(streamed_text)
                time.sleep(0.01)

            response_time = round(time.time() - start_time, 2)
            logger.info(f"Response generated in {response_time} seconds")

        add_assistant_message(answer)

    except Exception as e:
        logger.exception("Query execution failed")
        with st.chat_message("assistant"):
            st.error(f"Query Error: {e}")


def main():
    set_page_config()
    init_app()

    render_header()
    with st.sidebar:
        top_k = render_sidebar()

    render_chat_history()

    query = st.chat_input("Ask something about your documents...")
    if query:
        handle_query(query)


if __name__ == "__main__":
    main()
