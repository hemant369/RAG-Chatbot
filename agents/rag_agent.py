from langchain_ollama import ChatOllama

from langchain.agents import create_agent

from agents.tools import (
    search_documents,
    calculate,
    list_documents,
)

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)


def get_agent():

    return create_agent(
        model=llm,
        tools=[
            search_documents,
            calculate,
            list_documents,
        ],
    )