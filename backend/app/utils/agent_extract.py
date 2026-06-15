def extract_agent_answer(response) -> str:
    if isinstance(response, str):
        return response
    if hasattr(response, "content"):
        content = getattr(response, "content")
        if isinstance(content, str) and content.strip():
            return content
    if isinstance(response, dict):
        for key in ("output", "answer", "final_answer", "content"):
            value = response.get(key)
            if isinstance(value, str) and value.strip():
                return value
        messages = response.get("messages")
        if isinstance(messages, list):
            for message in reversed(messages):
                content = message.get("content") if isinstance(message, dict) else getattr(message, "content", None)
                if isinstance(content, str) and content.strip():
                    return content
    return "No response generated"