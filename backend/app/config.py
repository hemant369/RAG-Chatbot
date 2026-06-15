import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM Settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:3b")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "300.0"))

    # Retrieval Settings
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "10"))
    RERANKER_TOP_N: int = int(os.getenv("RERANKER_TOP_N", "3"))
    BM25_CORPUS_LIMIT: int = int(os.getenv("BM25_CORPUS_LIMIT", "1000"))

    # Embedding Model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")

    # Logs
    MAX_LOG_LINES: int = int(os.getenv("MAX_LOG_LINES", "100"))

    # Database
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "../db/chroma_db")

    # API
    PORT: int = int(os.getenv("PORT", "8000"))
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    # Web Search
    WEB_SEARCH_MAX_RESULTS: int = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))


settings = Settings()
