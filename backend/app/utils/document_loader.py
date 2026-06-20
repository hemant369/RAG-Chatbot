import tempfile
import os

from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader
from app.utils.logger import logger


def load_uploaded_document(uploaded_file):
    temp_path = None
    try:
        logger.info(f"Loading uploaded document: {uploaded_file.name}")

        suffix = os.path.splitext(uploaded_file.name)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        logger.debug(f"Temporary file created at: {temp_path}")

        file_extractor = {".pdf": PyMuPDFReader()}

        documents = SimpleDirectoryReader(
            input_files=[temp_path],
            file_extractor=file_extractor
        ).load_data()

        if not documents:
            raise ValueError(
                f"No content extracted from '{uploaded_file.name}'. "
                "The file may be scanned/image-based or corrupted."
            )

        logger.info(f"Loaded {len(documents)} document(s) from {uploaded_file.name}")
        return documents

    except Exception as e:
        logger.exception(f"Failed to load uploaded document: {uploaded_file.name}")
        raise

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
            logger.debug(f"Temporary file removed: {temp_path}")