from llama_index.core.postprocessor import SentenceTransformerRerank
from app.utils.logger import logger
from app.config import settings


def _load_reranker() -> SentenceTransformerRerank:
    try:
        reranker = SentenceTransformerRerank(
            model=settings.RERANKER_MODEL,
            top_n=settings.RERANKER_TOP_N,
        )
        logger.info(f"Reranker model initialized: {settings.RERANKER_MODEL} (top_n={settings.RERANKER_TOP_N})")
        return reranker
    except Exception as e:
        logger.error(f"Reranker initialization failed: {e}")
        raise


reranker = _load_reranker()