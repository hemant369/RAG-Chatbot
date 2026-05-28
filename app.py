import time
import streamlit as st

from utils.document_loader import (
    load_uploaded_document,
)

from utils.category_detector import (
    detect_category,
    detect_query_category,
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

uploaded_file = st.file_uploader(
    "Upload Document",
    type=[
        "pdf",
        "txt",
        "md",
        "csv",
        "json",
        "yaml",
        "yml"
    ]
)


# ============================================
# DOCUMENT INDEXING
# ============================================

if uploaded_file and st.button(
    "Load Document"
):

    with st.spinner(
        "Indexing document..."
    ):

        documents = load_uploaded_document(
            uploaded_file
        )

        full_text = " ".join(
            [doc.text for doc in documents]
        )

        detected_category = detect_category(
            full_text
        )

        st.success(
            f"Detected Category: "
            f"{detected_category}"
        )

        for doc in documents:

            doc.metadata = {
                "file_name": uploaded_file.name,
                "category": detected_category,
            }

        create_index(documents)

        st.success(
            "Document Indexed Successfully!"
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

        start_time = time.time()

        query_category = detect_query_category(
            query
        )

        st.info(
            f"Detected Query Category: "
            f"{query_category}"
        )

        query_engine = get_query_engine(
            category=query_category,
            top_k=top_k,
        )

        response = query_engine.query(query)

        response_time = round(
            time.time() - start_time,
            2
        )

        st.subheader("📌 Answer")

        st.write(str(response))

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

        st.caption(
            f"⏱ Response Time: "
            f"{response_time} seconds"
        )