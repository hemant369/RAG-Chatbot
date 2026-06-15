import tempfile
import os

from llama_index.core import (
    SimpleDirectoryReader,
)

from app.utils.logger import logger


def load_uploaded_document(uploaded_file):

    try:
        logger.info(
            f"Loading uploaded document: {uploaded_file.name}"
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(
                uploaded_file.name
            )[1]
        ) as tmp_file:

            tmp_file.write(
                uploaded_file.read()
            )

            temp_path = tmp_file.name

        logger.debug(
            f"Temporary file created at: {temp_path}"
        )

        documents = SimpleDirectoryReader(
            input_files=[temp_path]
        ).load_data()

        logger.info(
            f"Loaded {len(documents)} document(s) from {uploaded_file.name}"
        )

        return documents

    except Exception as e:
        logger.exception(
            f"Failed to load uploaded document: {uploaded_file.name}"
        )
        raise