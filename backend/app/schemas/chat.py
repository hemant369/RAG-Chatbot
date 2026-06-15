from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ToolCall(BaseModel):
    name: str
    input: str
    output: str

class AgentReasoning(BaseModel):
    thought: Optional[str] = None
    tool_calls: List[ToolCall] = []
    final_answer: str

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str
    agent_reasoning: AgentReasoning
    sources: List[Dict[str, Any]] = []

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]