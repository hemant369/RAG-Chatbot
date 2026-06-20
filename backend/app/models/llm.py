from llama_index.llms.ollama import Ollama
from langchain_ollama import ChatOllama

from app.config import settings

# LlamaIndex LLM (for query engine)
llm = Ollama(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    request_timeout=settings.LLM_TIMEOUT,
)

# LangChain LLM (for agents)
chat_llm = ChatOllama(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    request_timeout=settings.LLM_TIMEOUT,
)