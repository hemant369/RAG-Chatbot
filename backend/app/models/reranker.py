from llama_index.core.postprocessor import SentenceTransformerRerank
from app.utils.logger import logger


def _load_reranker() -> SentenceTransformerRerank:
    try:
        reranker = SentenceTransformerRerank(
            model="BAAI/bge-reranker-base",
            top_n=3,
        )
        logger.info("Reranker model initialized: BAAI/bge-reranker-base")
        return reranker
    except Exception as e:
        logger.error(f"Reranker initialization failed: {e}")
        raise


reranker = _load_reranker()