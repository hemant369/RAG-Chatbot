import hashlib

from database.chroma_db import (
    chroma_collection,
)


def generate_file_hash(uploaded_file):

    return hashlib.md5(
        uploaded_file.getvalue()
    ).hexdigest()


def document_exists(file_hash):

    results = chroma_collection.get(
        where={
            "file_hash": file_hash
        }
    )

    return len(results["ids"]) > 0