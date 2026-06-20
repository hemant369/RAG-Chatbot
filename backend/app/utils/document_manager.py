import hashlib
import os
from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader

from app.database.chroma_db import chroma_collection
from app.utils.logger import logger
from app.utils.query_engine import create_index


class DocumentManager:
    def __init__(self):
        self.collection = chroma_collection

    def generate_file_hash(self, file_path: str) -> str:
        """Generate SHA256 hash for file deduplication."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()
        logger.debug(f"Generated SHA256 hash: {file_hash} for {file_path}")
        return file_hash

    def document_exists(self, file_hash: str) -> bool:
        results = self.collection.get(where={"file_hash": file_hash})
        exists = len(results["ids"]) > 0
        logger.info(f"Document exists check for hash {file_hash}: {exists}")
        return exists

    def _load_documents(self, file_path: str, file_hash: str):
        """Load documents directly from file path using PyMuPDF."""
        suffix = Path(file_path).suffix.lower()

        file_extractor = {".pdf": PyMuPDFReader()}

        documents = SimpleDirectoryReader(
            input_files=[file_path],
            file_extractor=file_extractor,
        ).load_data()

        if not documents:
            raise ValueError(
                f"No content extracted from '{file_path}'. "
                "File may be scanned/image-based or corrupted."
            )

        for doc in documents:
            doc.metadata["file_hash"] = file_hash

        logger.info(f"Loaded {len(documents)} document(s) from {file_path}")
        return documents

    def index_document(self, file_path: str) -> str:
        file_hash = self.generate_file_hash(file_path)

        if self.document_exists(file_hash):
            logger.info(f"Document already indexed: {file_path}")
            return file_hash

        documents = self._load_documents(file_path, file_hash)
        create_index(documents)
        logger.info(f"Document indexed: {file_path} -> {file_hash}")
        return file_hash

    def list_documents(self):
        results = self.collection.get()
        seen = {}

        for metadata in results.get("metadatas", []):
            if not metadata:
                continue
            file_hash = metadata.get("file_hash")
            file_name = metadata.get("file_name")
            if not file_hash or not file_name:
                continue
            if file_hash not in seen:
                seen[file_hash] = {
                    "id": file_hash,
                    "filename": file_name,
                    "file_hash": file_hash,
                    "chunk_count": 0,
                }
            seen[file_hash]["chunk_count"] += 1

        return list(seen.values())

    def get_document(self, doc_id: str):
        results = self.collection.get(where={"file_hash": doc_id})
        if not results["ids"]:
            return None

        # ChromaDB already filtered by file_hash, first result is sufficient
        metadata = results["metadatas"][0] if results.get("metadatas") else {}

        return {
            "id": doc_id,
            "filename": metadata.get("file_name", ""),
            "file_hash": doc_id,
            "chunks": len(results["ids"]),
        }

    def delete_document(self, doc_id: str) -> bool:
        if not self.document_exists(doc_id):
            return False

        self.collection.delete(where={"file_hash": doc_id})
        logger.info(f"Document deleted: {doc_id}")
        return True