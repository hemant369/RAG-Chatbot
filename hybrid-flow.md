# Hybrid-Flow Diagram

```text

search_documents(question)
            │
            ▼
     get_query_engine()
            │
            ▼
 ┌──────────────────────┐
 │ VectorStoreIndex     │
 │ (ChromaDB)           │
 └──────────┬───────────┘
            │
            ▼
     Vector Retriever
     similarity_top_k=10
            │
            │
            │
            ▼

 ┌──────────────────────┐
 │ Load All Chunks      │
 │ From ChromaDB        │
 └──────────┬───────────┘
            │
            ▼
      TextNode Creation
            │
            ▼
      BM25 Retriever
      similarity_top_k=10
            │
            │
            │
            ▼

 ┌─────────────────────────────────┐
 │      QueryFusionRetriever       │
 │                                 │
 │  Vector Retriever Results       │
 │               +                 │
 │      BM25 Retriever Results     │
 │                                 │
 │ Reciprocal Rank Fusion (RRF)    │
 └───────────────┬─────────────────┘
                 │
                 ▼
         Top Retrieved Chunks
                 │
                 ▼
 ┌───────────────────────────────┐
 │          Reranker             │
 │                               │
 │ Re-ranks retrieved chunks     │
 │ based on semantic relevance   │
 └───────────────┬───────────────┘
                 │
                 ▼
        Best Context Chunks
                 │
                 ▼
 ┌───────────────────────────────┐
 │             LLM               │
 │                               │
 │ Question + Context Chunks     │
 └───────────────┬───────────────┘
                 │
                 ▼
           Final Answer

```