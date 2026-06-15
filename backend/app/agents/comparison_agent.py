from textwrap import dedent
from app.utils.logger import logger
from app.models.llm import chat_llm as llm


def compare_answers(question: str, document_answer: str, web_answer: str) -> str:
    logger.info("Comparison Agent synthesizing answers")

    prompt = dedent(f"""
        You are a Comparison Agent. Your job is to analyze two sources of information
        and provide a clear, accurate, and well-reasoned final answer.

        User Question: {question}

        Document Answer (from RAG):
        {document_answer}

        Web Answer (from Internet):
        {web_answer}

        Instructions:
        - Identify agreements between both sources
        - Highlight any contradictions or differences
        - If the document is outdated compared to the web, mention it
        - Give a final synthesized answer that best answers the user's question

        Final Answer:
    """).strip()

    response = llm.invoke(prompt)
    result = response.content.strip()

    logger.info("Comparison Agent completed")
    return result