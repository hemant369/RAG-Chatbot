from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routes import chat, documents, logs
from app.utils.logger import setup_logger
from app.config import settings

load_dotenv()
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Warming up query engine...")
    try:
        from app.utils.query_engine import get_query_engine
        get_query_engine()
        logger.info("Query engine ready")
    except Exception as e:
        logger.warning(f"Query engine warmup skipped: {e}")

    yield

    # shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="RAG Agent API",
    description="FastAPI backend for Ollama + Qwen 2.5 RAG Agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
logger.info(f"CORS configured for origins: {settings.ALLOWED_ORIGINS}")

app.include_router(chat)
app.include_router(documents)
app.include_router(logs)


@app.get("/")
async def root():
    return {
        "message": "RAG Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.PORT,
        reload=True,
    )