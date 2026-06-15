from llama_index.llms.ollama import Ollama

from app.utils.logger import logger

llm = Ollama(
    model="qwen2.5:3b",
    request_timeout=300.0,
)
logger.info("LLM model initialized: qwen2.5:3b")