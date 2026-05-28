from llama_index.llms.ollama import Ollama

llm = Ollama(
    model="qwen2.5:3b",
    request_timeout=120.0
)