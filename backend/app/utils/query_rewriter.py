from app.models.llm import llm
from app.utils.logger import logger


def rewrite_query(
    question: str,
    chat_context: str,
) -> str:

    logger.info("Rewriting user query for standalone execution")

    prompt = f"""
    You are an enterprise query rewriting assistant.
    Your task is to convert follow-up questions into standalone questions.

    Instructions:
    1. If the question is already understandable by itself, return it unchanged.
    2. If the question depends on previous conversation, rewrite it into a standalone question.
    3. Preserve all filenames, document names, people, dates, numbers, IDs, acronyms, and technical terms exactly.
    4. Do NOT invent information that does not appear in the conversation.
    5. Do NOT add explanations, assumptions, or extra context.
    6. Keep the rewritten question concise.
    7. If there is insufficient context, return the original question unchanged.
    8. Return ONLY the rewritten question.

    Previous Conversation:
    {chat_context}

    Current Question:
    {question}

    Rewritten Question:
    """

    response = llm.complete(prompt)

    rewritten = str(response)
    logger.debug(f"Rewritten query: {rewritten}")
    return rewritten