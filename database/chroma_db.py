import chromadb

from llama_index.vector_stores.chroma import (
    ChromaVectorStore,
)

from llama_index.core import StorageContext


# Persistent Chroma Client
db = chromadb.PersistentClient(
    path="db/chroma_db"
)

# Collection
chroma_collection = db.get_or_create_collection(
    "documents"
)

# Vector Store
vector_store = ChromaVectorStore(
    chroma_collection=chroma_collection
)

# Storage Context
storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)