import tempfile
import os

from llama_index.core import (
    SimpleDirectoryReader,
    Document,
)

from app.utils.logger import logger
from app.config import settings


def _load_pdf_with_markdown(file_path: str, file_name: str) -> list:
    """
    Load PDF using pymupdf4llm to extract markdown-formatted text.

    This preserves document structure like headers, tables, lists, etc.
    """
    try:
        import pymupdf4llm

        logger.info(f"Loading PDF with markdown extraction: {file_name}")

        # Extract markdown from PDF
        md_text = pymupdf4llm.to_markdown(file_path)

        logger.debug(f"Extracted {len(md_text)} characters of markdown from {file_name}")

        # Split markdown into chunks by pages if possible
        # pymupdf4llm includes page markers in format: -----\n\n
        pages = md_text.split("-----\n\n") if "-----\n\n" in md_text else [md_text]

        documents = []
        for page_num, page_content in enumerate(pages, start=1):
            if page_content.strip():  # Skip empty pages
                doc = Document(
                    text=page_content.strip(),
                    metadata={
                        "file_name": file_name,
                        "page_label": str(page_num),
                        "format": "markdown",
                        "source": "pymupdf4llm"
                    }
                )
                documents.append(doc)

        logger.info(f"Loaded {len(documents)} page(s) from {file_name} with markdown formatting")
        return documents

    except ImportError:
        logger.warning("pymupdf4llm not installed, falling back to standard loader")
        return None
    except Exception as e:
        logger.warning(f"Markdown extraction failed for {file_name}: {str(e)}, falling back to standard loader")
        return None


def load_uploaded_document(uploaded_file):
    """
    Load uploaded document with support for multiple formats.

    For PDFs:
    - If USE_MARKDOWN_EXTRACTION is True, uses pymupdf4llm to extract markdown
    - Falls back to standard loader if markdown extraction fails

    For other formats (TXT, MD, CSV, JSON, YAML):
    - Uses LlamaIndex SimpleDirectoryReader
    """
    try:
        logger.info(f"Loading uploaded document: {uploaded_file.name}")

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        logger.debug(f"Temporary file created at: {temp_path}")

        # Check if it's a PDF and markdown extraction is enabled
        is_pdf = uploaded_file.name.lower().endswith('.pdf')

        if is_pdf and settings.USE_MARKDOWN_EXTRACTION:
            logger.info("Attempting markdown extraction for PDF")
            documents = _load_pdf_with_markdown(temp_path, uploaded_file.name)

            if documents:
                # Successfully loaded with markdown
                logger.info(f"Successfully extracted {len(documents)} pages with markdown formatting")
                return documents
            else:
                # Fall back to standard loader
                logger.info("Falling back to standard PDF loader")

        # Standard loader for non-PDF files or fallback
        documents = SimpleDirectoryReader(
            input_files=[temp_path]
        ).load_data()

        # Add metadata if not already present
        for doc in documents:
            if "file_name" not in doc.metadata:
                doc.metadata["file_name"] = uploaded_file.name
            if "format" not in doc.metadata:
                doc.metadata["format"] = "standard"

        logger.info(f"Loaded {len(documents)} document(s) from {uploaded_file.name}")

        return documents

    except Exception as e:
        logger.exception(f"Failed to load uploaded document: {uploaded_file.name}")
        raise
    finally:
        # Clean up temporary file
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug(f"Cleaned up temporary file: {temp_path}")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temp file: {cleanup_error}")