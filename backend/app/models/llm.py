from llama_index.llms.ollama import Ollama
from langchain_ollama import ChatOllama

from app.config import settings
from app.utils.logger import logger, is_main_process

# LlamaIndex LLM (for query engine)
llm = Ollama(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    request_timeout=settings.LLM_TIMEOUT,
)

# LangChain LLM (for agents) - Single shared instance
chat_llm = ChatOllama(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    request_timeout=settings.LLM_TIMEOUT,
)

if is_main_process():
    logger.info(f"LLM models initialized: {settings.LLM_MODEL}")