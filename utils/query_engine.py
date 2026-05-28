from llama_index.core import (
    VectorStoreIndex,
)

from llama_index.core.vector_stores import (
    MetadataFilters,
    ExactMatchFilter,
)

from database.chroma_db import (
    storage_context,
    vector_store,
)

from models.embedding_model import (
    embed_model,
)

from models.llm import llm

from models.reranker import reranker


def create_index(documents):

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    return index


def get_query_engine(
    category=None,
    top_k=10,
):

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )

    try:

        if category:

            filters = MetadataFilters(
                filters=[
                    ExactMatchFilter(
                        key="category",
                        value=category
                    )
                ]
            )

            retriever = index.as_retriever(
                similarity_top_k=top_k,
                filters=filters
            )

            nodes = retriever.retrieve(
                "test"
            )

            # No matching category
            if len(nodes) == 0:

                print(
                    "No filtered nodes found. "
                    "Using global search."
                )

                query_engine = index.as_query_engine(
                    llm=llm,
                    similarity_top_k=top_k,
                    node_postprocessors=[
                        reranker
                    ]
                )

            else:

                query_engine = index.as_query_engine(
                    llm=llm,
                    similarity_top_k=top_k,
                    filters=filters,
                    node_postprocessors=[
                        reranker
                    ]
                )

        else:

            query_engine = index.as_query_engine(
                llm=llm,
                similarity_top_k=top_k,
                node_postprocessors=[
                    reranker
                ]
            )

        return query_engine

    except Exception as e:

        print(f"Query Engine Error: {e}")

        return index.as_query_engine(
            llm=llm,
            similarity_top_k=top_k,
            node_postprocessors=[
                reranker
            ]
        )
