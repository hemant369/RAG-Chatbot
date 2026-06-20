from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.config import settings

embed_model = HuggingFaceEmbedding(
    model_name=settings.EMBEDDING_MODEL
)