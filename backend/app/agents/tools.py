from app.utils.query_engine import get_query_engine
from app.utils.document_manager import DocumentManager
from app.utils.logger import logger
from app.config import settings

from langchain_core.tools import tool
from ddgs import DDGS


# ============================================
# RAG SEARCH TOOL
# ============================================

@tool
def search_documents(question: str) -> str:
    """
    Search all uploaded documents (PDFs, TXT, MD, CSV, JSON, YAML).

    Use this tool when the user asks about:
    - Document content, summaries, or specific information in uploaded files
    - Reports, contracts, policies, manuals, or any uploaded materials
    - Company-specific internal data or proprietary information
    - Questions that explicitly reference "my document", "the file", "uploaded PDF", etc.
    - Historical data that was uploaded by the user

    Examples:
    - "What does my contract say about termination?"
    - "Summarize the Q4 report I uploaded"
    - "What are the key points in my document?"

    Do NOT use for:
    - Current events, news, or real-time information
    - Public figures or companies (unless specifically about uploaded documents)
    - Questions requiring up-to-date web information

    Returns: Answer with source citations (filename and page numbers)
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
    List all documents that have been uploaded and indexed in the system.

    Use this tool when the user asks:
    - "What documents do I have?"
    - "Which files are available?"
    - "Show me my uploaded documents"
    - "List all indexed files"
    - "What can I search in my documents?"

    Returns: List of all indexed document filenames
    """
    logger.info("Tool list_documents called")

    try:
        doc_manager = DocumentManager()
        documents = doc_manager.list_documents()

        if not documents:
            logger.info("No documents indexed")
            return "No documents indexed."

        # Extract unique filenames
        files = [doc["filename"] for doc in documents]

        logger.info(f"list_documents returned {len(files)} files")
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
    Search the internet for current, real-time, and public information.

    Use this tool when the user asks about:
    - Current events, breaking news, or recent developments
    - Public figures (CEOs, founders, politicians, celebrities)
    - Companies and their current status, stock prices, or recent announcements
    - Technologies, products, or services and their latest versions
    - Real-world facts, statistics, or data not likely to be in uploaded documents
    - Questions requiring up-to-date information (weather, sports scores, etc.)
    - Verification of information against current public sources

    Examples:
    - "Who is the current CEO of Apple?"
    - "What's the latest news about artificial intelligence?"
    - "What happened in the 2026 Olympics?"
    - "What is the stock price of Tesla today?"

    Use with document search for comparison queries:
    - "Compare the CEO in my document with Apple's current CEO" (use search_documents first, then web_search)
    - "Is the information in my document still accurate?" (search docs, then verify with web)

    Returns: Search results with titles, content snippets, and URLs
    """

    logger.info(f"Tool web_search called with query: {query}")

    try:

        results = []

        with DDGS() as ddgs:

            search_results = list(
                ddgs.text(
                    query,
                    max_results=settings.WEB_SEARCH_MAX_RESULTS,
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