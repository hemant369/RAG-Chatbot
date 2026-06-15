from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, AgentReasoning
from app.utils.logger import setup_logger
from app.core.agentic_rag import AgenticRAG


router = APIRouter(prefix="/chat", tags=["chat"])
logger = setup_logger(__name__)

agent = AgenticRAG()


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    try:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.chat_history
        ]

        result = agent.run(
            query=request.query,
            chat_history=history,
        )

        reasoning = AgentReasoning(
            thought="\n".join(result.get("trace", [])),
            tool_calls=[],
            final_answer=result["final_answer"],
        )

        return ChatResponse(
            answer=result["final_answer"],
            agent_reasoning=reasoning,
            sources=result.get("sources", []),
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/clear")
async def clear_history():
    return {"message": "No server-side history to clear. History is managed client-side."}


@router.get("/health")
async def health_check():
    try:
        _ = agent
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")