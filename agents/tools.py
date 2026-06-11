from utils.query_engine import (
    get_query_engine,
)

from database.chroma_db import (
    chroma_collection,
)

from langchain_core.tools import tool


# ============================================
# RAG SEARCH TOOL
# ============================================

@tool
def search_documents(
    question: str,
) -> str:
    
    """
    Search all indexed documents.

    Use this tool whenever the user asks about
    document content, quotes text from a document,
    requests document information, asks for a summary,
    asks whether something exists in a document,
    or refers to uploaded documents in any way.
    """

    try:

        query_engine = get_query_engine()

        response = query_engine.query(
            question
        )

        return response.response

    except Exception as e:

        return (
            f"Search Tool Error: {str(e)}"
        )


# ============================================
# CALCULATOR TOOL
# ============================================

@tool
def calculate(
    expression: str,
) -> str:
    
    """
    Perform mathematical calculations.
    """

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {},
        )

        return str(result)

    except Exception as e:

        return (
            f"Calculator Error: {str(e)}"
        )


# ============================================
# LIST DOCUMENTS TOOL
# ============================================

@tool
def list_documents() -> str:

    """
    List all indexed documents.
    """

    try:

        results = chroma_collection.get()

        if len(results["ids"]) == 0:

            return (
                "No documents indexed."
            )

        files = set()

        for metadata in results[
            "metadatas"
        ]:

            if (
                metadata
                and "file_name"
                in metadata
            ):

                files.add(
                    metadata[
                        "file_name"
                    ]
                )

        if len(files) == 0:

            return (
                "No documents found."
            )

        return "\n".join(
            sorted(files)
        )

    except Exception as e:

        return (
            f"Document Tool Error: {str(e)}"
        )