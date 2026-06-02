import time
import streamlit as st

from utils.document_loader import (
    load_uploaded_document,
)

from utils.document_manager import (
    generate_file_hash,
    document_exists,
)

from utils.query_engine import (
    create_index,
    get_query_engine,
)


# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Advanced RAG App",
    layout="wide"
)

st.title("📄 Advanced Local RAG App")



# ============================================
# SIDEBAR
# ============================================

top_k = st.sidebar.slider(
    "Similarity Top K",
    1,
    20,
    10,
    key="top_k_slider"
)


# ============================================
# FILE UPLOAD
# ============================================

uploaded_files = st.file_uploader(
    "Upload Documents",
    type=[
        "pdf",
        "txt",
        "md",
        "csv",
        "json",
        "yaml",
        "yml"
    ],
    accept_multiple_files=True
)


# ============================================
# DOCUMENT INDEXING
# ============================================

if uploaded_files and st.button(
    "Load Document"
):

    with st.spinner(
        "Indexing document..."
    ):

        try:

            for uploaded_file in uploaded_files:

                # Load documents
                documents = load_uploaded_document(
                    uploaded_file
                )

                # Generate document hash
                file_hash = generate_file_hash(
                    uploaded_file
                )

                # Check if already indexed
                if document_exists(file_hash):
                    st.warning(
                        f"{uploaded_file.name} already indexed."
                        )

                    continue

                for doc in documents:

                    doc.metadata = {
                        "file_name": uploaded_file.name,
                        "file_hash": file_hash,
                    }

                create_index(documents)

                st.success(
                    f"✅ {uploaded_file.name} indexed."
                )

        except Exception as e:

            st.error(
                f"Error: {str(e)}"
            )

# ============================================
# USER QUERY
# ============================================

query = st.text_input(
    "Ask a question"
)


# ============================================
# QUERYING
# ============================================

if query:

        with st.spinner(
            "Generating Answer..."
        ):

            try:

                start_time = time.time()

                # Create hybrid query engine
                query_engine = get_query_engine(
                    top_k=top_k,
                )

                # Query
                response = query_engine.query(
                    query
                )

                response_time = round(
                    time.time() - start_time,
                    2
                )

                # ====================================
                # ANSWER
                # ====================================

                st.subheader("📌 Answer")

                if not response.response.strip():

                    st.warning(
                        "No response generated."
                    )

                else:

                    st.write(
                        response.response
                    )

                # ====================================
                # RETRIEVED CHUNKS
                # ====================================

                st.subheader(
                    "📚 Retrieved Chunks"
                )

                for i, node in enumerate(
                    response.source_nodes
                ):

                    st.markdown(
                        f"### Chunk {i+1}"
                    )

                    st.write(
                        node.node.text[:500]
                    )

                    st.write(
                        node.node.metadata
                    )

                    st.markdown("---")

                # ====================================
                # RESPONSE TIME
                # ====================================

                st.caption(
                    f"⏱ Response Time: "
                    f"{response_time} seconds"
                )

            except Exception as e:

                st.error(f"Query Error: {e}")