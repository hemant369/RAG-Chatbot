from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.retrievers.bm25 import BM25Retriever

from app.database.chroma_db import vector_store, storage_context, chroma_collection
from app.models.embedding_model import embed_model
from app.models.llm import llm
from app.models.reranker import reranker
from app.utils.logger import logger


_query_engine = None
_bm25_nodes = None  # cached separately


def _load_bm25_nodes() -> list:
    global _bm25_nodes
    if _bm25_nodes is not None:
        return _bm25_nodes

    logger.info("Loading BM25 corpus from ChromaDB")
    results = chroma_collection.get(limit=500)  # safety limit

    if not results["ids"]:
        raise ValueError("No documents found in vector database.")

    _bm25_nodes = [
        TextNode(text=text, metadata=metadata)
        for text, metadata in zip(results["documents"], results["metadatas"])
    ]

    logger.info(f"BM25 corpus loaded: {len(_bm25_nodes)} nodes")
    return _bm25_nodes


def create_index(documents):
    logger.info(f"Creating index for {len(documents)} document(s)")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    logger.info("Index created successfully")

    # invalidate both caches on new upload
    global _query_engine, _bm25_nodes
    _query_engine = None
    _bm25_nodes = None  # force BM25 corpus rebuild

    return index


def _build_query_engine(top_k: int = 10) -> RetrieverQueryEngine:
    logger.info(f"Building query engine with top_k={top_k}")

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )

    vector_retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = _load_bm25_nodes()

    bm25_retriever = BM25Retriever.from_defaults(
        nodes=nodes,
        similarity_top_k=top_k,
    )

    fusion_retriever = QueryFusionRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        similarity_top_k=top_k,
        num_queries=1,
        mode="reciprocal_rerank",
        use_async=False,
        llm=llm,
        verbose=False,
    )

    return RetrieverQueryEngine.from_args(
        retriever=fusion_retriever,
        llm=llm,
        node_postprocessors=[reranker],
    )


def get_query_engine(top_k: int = 10) -> RetrieverQueryEngine:
    global _query_engine
    if _query_engine is None:
        _query_engine = _build_query_engine(top_k)
    return _query_engine