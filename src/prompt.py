def build_prompt(documents, user_query):
    context = ""

    for doc in documents:
        context += doc.page_content + "\n"

    prompt = f"""You are a helpful assistant. Use the following context to answer the question. 
    If you don't know the answer, say you don't know.
    Context: {context}

    Question: {user_query}
    """
    return prompt