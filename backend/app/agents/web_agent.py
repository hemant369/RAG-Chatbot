from textwrap import dedent
from langchain.agents import create_agent
from app.agents.tools import web_search
from app.utils.logger import logger
from app.models.llm import chat_llm as llm

SYSTEM_PROMPT = dedent("""
    You are a Web Research Agent.

    Use web_search whenever current or public information is required.

    Responsibilities:
    - Current events
    - Companies
    - CEOs
    - Technologies
    - Internet research

    Always use web_search when needed.
""").strip()


def get_web_agent():
    logger.info("Creating Web Agent")
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=SYSTEM_PROMPT,
    )