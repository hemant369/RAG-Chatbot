import time
import streamlit as st

from utils.chat_memory import (
    initialize_memory,
    add_user_message,
    add_assistant_message,
    get_chat_context,
    clear_memory,
)

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

from database.chroma_db import (
    chroma_collection,
)

from agents.rag_agent import (
    get_agent,
)


# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Advanced RAG Assistant",
    page_icon="🤖",
    layout="wide",
)

# ============================================
# CUSTOM CSS
# ============================================

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

# ============================================
# INITIALIZE MEMORY
# ============================================

initialize_memory()

# ============================================
# HEADER
# ============================================

st.title("🤖 Advanced RAG Assistant")
st.caption(
    "Upload documents and chat with your knowledge base"
)

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:

    st.header("📚 Knowledge Base")

    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=[
            "pdf",
            "txt",
            "md",
            "csv",
            "json",
            "yaml",
            "yml",
        ],
        accept_multiple_files=True,
    )

    if st.button("📥 Index Documents"):

        with st.spinner(
            "Indexing documents..."
        ):

            try:

                for uploaded_file in uploaded_files:

                    documents = load_uploaded_document(
                        uploaded_file
                    )

                    file_hash = generate_file_hash(
                        uploaded_file
                    )

                    if document_exists(
                        file_hash
                    ):

                        st.warning(
                            f"{uploaded_file.name} already indexed."
                        )

                        continue

                    for doc in documents:

                        doc.metadata = {
                            "file_name": uploaded_file.name,
                            "file_hash": file_hash,
                        }

                    create_index(
                        documents
                    )

                    st.success(
                        f"✅ {uploaded_file.name} indexed"
                    )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

    st.divider()

    top_k = st.slider(
        "Similarity Top K",
        min_value=1,
        max_value=20,
        value=10,
    )

    st.divider()

    st.subheader(
        "📄 Indexed Documents"
    )

    try:

        results = chroma_collection.get()

        if len(results["ids"]) > 0:

            unique_files = set()

            for meta in results.get(
                "metadatas",
                [],
            ):

                if (
                    meta
                    and "file_name" in meta
                ):

                    unique_files.add(
                        meta["file_name"]
                    )

            for file_name in sorted(
                unique_files
            ):

                st.success(
                    file_name
                )

        else:

            st.info(
                "No documents indexed."
            )

    except:

        st.info(
            "No documents indexed."
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🗑 Clear"
        ):

            clear_memory()
            st.rerun()

    with col2:

        if st.button(
            "🔄 New Chat"
        ):

            clear_memory()
            st.rerun()


# ============================================
# CHAT HISTORY
# ============================================

for msg in st.session_state.chat_history:

    with st.chat_message(
        msg["role"]
    ):

        st.markdown(
            msg["content"]
        )

# ============================================
# CHAT INPUT
# ============================================

query = st.chat_input(
    "Ask something about your documents..."
)

# ============================================
# QUERYING
# ============================================

if query:

    with st.chat_message(
        "user"
    ):

        st.markdown(
            query
        )

    add_user_message(
        query
    )

    try:

        start_time = time.time()

        # ====================================
        # LOAD AGENT
        # ====================================

        from agents.rag_agent import (
            get_agent,
        )

        agent = get_agent()

        # ====================================
        # CHAT MEMORY
        # ====================================

        chat_context = (
            get_chat_context()
        )

        enhanced_query = f"""
Previous Conversation:

{chat_context}

Current Question:

{query}
"""

        # ====================================
        # AGENT EXECUTION
        # ====================================

        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": enhanced_query,
                    }
                ]
            }
        )

        answer = str(response["messages"][-1].content)

        

        if not answer.strip():

            answer = (
                "No response generated."
            )

        # ====================================
        # ASSISTANT RESPONSE
        # ====================================

        with st.chat_message(
            "assistant"
        ):

            placeholder = st.empty()

            streamed_text = ""

            for word in answer.split():

                streamed_text += (
                    word + " "
                )

                placeholder.markdown(
                    streamed_text
                )

                time.sleep(0.01)

            response_time = round(
                time.time()
                - start_time,
                2,
            )

            with st.expander(
                "⚙️ Query Details"
            ):

                st.write(
                    f"Response Time: "
                    f"{response_time} sec"
                )

                st.write(
                    "Response generated "
                    "through Agentic RAG"
                )

        add_assistant_message(
            answer
        )

    except Exception as e:

        with st.chat_message(
            "assistant"
        ):

            st.error(
                f"Query Error: {e}"
            )