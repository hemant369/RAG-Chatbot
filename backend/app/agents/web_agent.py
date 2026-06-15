from textwrap import dedent
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from app.agents.tools import web_search
from app.utils.logger import logger


llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)

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