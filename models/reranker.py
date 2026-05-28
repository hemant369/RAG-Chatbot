from llama_index.core.postprocessor import (
    SentenceTransformerRerank,
)

reranker = SentenceTransformerRerank(
    model="BAAI/bge-reranker-base",
    top_n=3
)