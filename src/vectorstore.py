import os
from langchain_chroma import Chroma

DB_PATH = 'db/chroma_db'

def create_or_load_vectorstore(chunks, embeddings_models):
    if os.path.exists(DB_PATH):
        print("Loading existing vectorstore...")
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings_models)
        print("Vectorstore loaded.")
    else:
        print("Creating vectorstore...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings_models,
            persist_directory=DB_PATH,
        )
        print("Vectorstore created.")

    return vectorstore