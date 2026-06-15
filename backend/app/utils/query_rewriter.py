from app.models.llm import llm
from app.utils.logger import logger


def rewrite_query(
    question: str,
    chat_context: str,
) -> str:

    logger.info("Rewriting user query for standalone execution")

    prompt = f"""
    You are a query rewriting assistant.

    Previous Conversation:
    {chat_context}

    Question:
    {question}

    If the question is already standalone,
    return it unchanged.

    If it depends on previous conversation,
    rewrite it as a standalone question.

    Return only the final question.
    """

    response = llm.complete(prompt)

    rewritten = str(response)
    logger.debug(f"Rewritten query: {rewritten}")
    return rewritten