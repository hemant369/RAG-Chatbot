from app.utils.query_engine import get_query_engine
from app.database.chroma_db import chroma_collection
from app.utils.logger import logger

from langchain_core.tools import tool
from ddgs import DDGS


# ============================================
# RAG SEARCH TOOL
# ============================================

@tool
def search_documents(question: str) -> str:
    """
    Search all indexed documents.

    Use this tool whenever the user asks about:
    - Document content
    - Summaries
    - Reports
    - Contracts
    - Policies
    - Uploaded PDFs
    """
    logger.info(f"Tool search_documents called with question: {question}")

    try:
        query_engine = get_query_engine()
        response = query_engine.query(question)

        sources = []
        for node in response.source_nodes:
            file_name = node.metadata.get("file_name", "Unknown")
            page = node.metadata.get("page_label", "?")
            sources.append(f"{file_name} (page {page})")

        source_text = "\n".join(sources) if sources else "No sources found"

        logger.info("search_documents tool completed successfully")
        return f"{response.response}\n\nSources:\n{source_text}"

    except Exception as e:
        logger.exception("search_documents tool failed")
        return f"Search Tool Error: {str(e)}"


# ============================================
# LIST DOCUMENTS TOOL
# ============================================

@tool
def list_documents() -> str:
    """
    List all indexed documents.
    """

    logger.info("Tool list_documents called")

    try:

        results = chroma_collection.get()

        if not results["ids"]:

            logger.info("No documents indexed")

            return "No documents indexed."

        files = set()

        for metadata in results.get("metadatas", []):

            if metadata and "file_name" in metadata:

                files.add(metadata["file_name"])

        if not files:

            logger.info("No documents found in metadata")

            return "No documents found."

        logger.info(
            f"list_documents returned {len(files)} files"
        )

        return "\n".join(sorted(files))

    except Exception as e:

        logger.exception("list_documents tool failed")

        return f"Document Tool Error: {str(e)}"


# ============================================
# WEB SEARCH TOOL
# ============================================

@tool
def web_search(query: str) -> str:
    """
    Search the web for current information.

    Use for:
    - Current events
    - Recent news
    - Companies
    - CEOs
    - Technologies
    - Public internet information
    """

    logger.info(f"Tool web_search called with query: {query}")

    try:

        results = []

        with DDGS() as ddgs:

            search_results = list(
                ddgs.text(
                    query,
                    max_results=5,
                )
            )

        if not search_results:

            logger.info("web_search found no results")

            return "No web results found."

        for item in search_results:

            title = item.get("title", "")
            body = item.get("body", "")
            href = item.get("href", "")

            results.append(
                f"Title: {title}\n"
                f"Content: {body}\n"
                f"URL: {href}"
            )

        logger.info(
            f"web_search returned {len(results)} results"
        )

        return "\n\n".join(results)

    except Exception as e:

        logger.exception("web_search tool failed")

        return f"Web Search Error: {str(e)}"


# ============================================
# CALCULATOR TOOL (OPTIONAL)
# ============================================

# @tool
# def calculate(expression: str) -> str:
#     """
#     Perform mathematical calculations.
#     """
#
#     logger.info(
#         f"Tool calculate called with expression: {expression}"
#     )
#
#     try:
#
#         result = eval(
#             expression,
#             {"__builtins__": {}},
#             {},
#         )
#
#         logger.info(
#             "calculate tool completed successfully"
#         )
#
#         return str(result)
#
#     except Exception as e:
#
#         logger.exception(
#             "calculate tool failed"
#         )
#
#         return f"Calculator Error: {str(e)}"