# Flow Diagram

```text
USER QUERY
                                   │
                                   ▼
                         ┌─────────────────┐
                         │ Supervisor Agent │◄── has_documents flag
                         └─────────────────┘
                            │   invalid?
                            │      └──► Self Correction ──► default "rag"
                            │
        ┌───────────────┬───┴──────────────┬───────────────┐
        │               │                  │               │
        ▼               ▼                  ▼               ▼
    CHITCHAT          WEB                 RAG           COMPARE
        │               │                  │            (only if
        │               │                  │          docs exist)
        │               │                  │               │
        ▼               │            Query Rewrite    Query Rewrite
  LLM Chitchat          │                  │          ┌────┴────┐
        │               │                  ▼          ▼         ▼
        │               │        Hybrid Retrieval    RAG       WEB
        │               │                  │        Agent     Agent
        │               │                  │          │         │
        │               │                  ▼          ▼         ▼
        │               │            RAG Answer   RAG Ans   Web Ans
        │               │                  │          │         │
        │               ▼                  │          └────┬────┘
        │          Query Rewrite           │               ▼
        │               │                 │       Comparison Agent
        │               ▼                 │               │
        │           Web Agent             │               ▼
        │               │                 │         Final Answer
        │               ▼                 │               │
        │          Web Answer             │               │
        │               │                 │               │
        └───────────────┴─────────────────┴───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │    Logging + Evaluation   │
                    │  (route, trace, sources)  │
                    └──────────────────────────┘
```
# Component Reference

## Agentic RAG

|        Component         |                                             What it does                                                                 |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------|
| **User Query**           | Raw message from the user, passed as-is to the Supervisor Agent.                                                         |
| **Supervisor Agent**     | Reads the query and checks whether documents exist. Decides one of four routes: `RAG`, `WEB`, `COMPARE`, or `CHITCHAT`.  |
| **Self Correction**      | If the Supervisor LLM returns an invalid route, it is asked to correct itself.                                           |
| **has_documents Flag**   | A boolean value passed from the application that prevents `RAG` or `COMPARE` routes when no documents are uploaded.      |
| **Query Rewriter**       | Uses chat history to convert vague follow-up questions into standalone questions.                                        |
| **Hybrid Retrieval**     | Combines semantic search (Vector Search) and exact keyword search (BM25) over uploaded documents                         |
| **RAG Agent**            | Retrieves relevant chunks from uploaded documents and generates a grounded answer with source citations.                 |
| **Web Agent**            | Performs web search, fetches results, and uses the LLM to summarize them into a clean answer.                            |
| **Comparison Agent**     | Takes both the RAG answer and Web answer, resolves conflicts, and generates one consolidated response.                   |
| **LLM Chitchat**         | Direct LLM response without retrieval or query rewriting. Used for greetings and casual conversations.                   |
| **Logging + Evaluation** | Records the selected route, execution trace, and sources used during answer generation.                                  |

