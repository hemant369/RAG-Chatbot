from llama_index.core import (
    VectorStoreIndex,
)

from llama_index.core.schema import (
    TextNode,
)

from llama_index.core.retrievers import (
    QueryFusionRetriever,
)

from llama_index.core.query_engine import (
    RetrieverQueryEngine,
)

from llama_index.retrievers.bm25 import (
    BM25Retriever,
)

from database.chroma_db import (
    vector_store,
    storage_context,
    chroma_collection,
)

from models.embedding_model import (
    embed_model,
)

from models.llm import (
    llm,
)

from models.reranker import (
    reranker,
)


# ============================================
# CREATE INDEX
# ============================================

def create_index(documents):

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    return index


# ============================================
# GET QUERY ENGINE
# ============================================

def get_query_engine(
    top_k=10,
):

    # ----------------------------------------
    # VECTOR INDEX
    # ----------------------------------------

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )

    # ----------------------------------------
    # VECTOR RETRIEVER
    # ----------------------------------------

    vector_retriever = index.as_retriever(
        similarity_top_k=top_k
    )

    # ----------------------------------------
    # LOAD CHUNKS FROM CHROMA
    # ----------------------------------------

    results = chroma_collection.get()
    
    if len(results["ids"]) == 0:
        raise ValueError(
            "No documents found in vector database."
        )

    nodes = []

    documents = results.get(
        "documents",
        []
    )

    metadatas = results.get(
        "metadatas",
        []
    )

    for text, metadata in zip(
        documents,
        metadatas,
    ):

        node = TextNode(
            text=text,
            metadata=metadata,
        )

        nodes.append(node)

    # ----------------------------------------
    # BM25 RETRIEVER
    # ----------------------------------------

    bm25_retriever = BM25Retriever.from_defaults(
        nodes=nodes,
        similarity_top_k=top_k,
    )

    # ----------------------------------------
    # HYBRID FUSION RETRIEVER
    # ----------------------------------------

    fusion_retriever = QueryFusionRetriever(
        retrievers=[
            vector_retriever,
            bm25_retriever,
        ],
        similarity_top_k=top_k,
        num_queries=1,
        mode="reciprocal_rerank",
        use_async=False,
        llm=llm,
        verbose=True,
    )

    # ----------------------------------------
    # QUERY ENGINE
    # ----------------------------------------

    query_engine = RetrieverQueryEngine.from_args(
        retriever=fusion_retriever,
        llm=llm,
        node_postprocessors=[
            reranker,
        ],
    )

    return query_engine