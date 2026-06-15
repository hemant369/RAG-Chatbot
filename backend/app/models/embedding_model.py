from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.utils.logger import logger
from app.config import settings

embed_model = HuggingFaceEmbedding(
    model_name=settings.EMBEDDING_MODEL
)
logger.info(f"Embedding model initialized: {settings.EMBEDDING_MODEL}")