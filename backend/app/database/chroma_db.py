import os
from dotenv import load_dotenv
import chromadb

from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext

from app.utils.logger import logger

load_dotenv()

chroma_path = os.getenv("CHROMA_DB_PATH", "../db/chroma_db")

db = chromadb.PersistentClient(path=chroma_path)
chroma_collection = db.get_or_create_collection("documents")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

storage_context = StorageContext.from_defaults(vector_store=vector_store)