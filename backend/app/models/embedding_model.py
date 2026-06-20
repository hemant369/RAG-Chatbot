from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.utils.logger import logger, is_main_process
from app.config import settings

embed_model = HuggingFaceEmbedding(
    model_name=settings.EMBEDDING_MODEL
)

if is_main_process():
    logger.info(f"Embedding model initialized: {settings.EMBEDDING_MODEL}")