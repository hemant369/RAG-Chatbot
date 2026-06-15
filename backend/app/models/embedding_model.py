from llama_index.embeddings.huggingface import (
    HuggingFaceEmbedding,
)

from app.utils.logger import logger

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)
logger.info("Embedding model initialized: BAAI/bge-small-en-v1.5")