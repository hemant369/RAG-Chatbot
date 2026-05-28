import tempfile
import os

from llama_index.core import (
    SimpleDirectoryReader,
)


def load_uploaded_document(uploaded_file):

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

    documents = SimpleDirectoryReader(
        input_files=[temp_path]
    ).load_data()

    return documents