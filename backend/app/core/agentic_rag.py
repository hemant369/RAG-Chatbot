from textwrap import dedent
from langchain.agents import create_agent
from app.agents.tools import search_documents, list_documents, web_search
from app.utils.query_rewriter import rewrite_query
from app.utils.agent_extract import extract_agent_answer
from app.utils.logger import logger
from app.models.llm import chat_llm as llm


# Comprehensive system prompt for single agentic RAG system
AGENTIC_RAG_SYSTEM_PROMPT = dedent("""
    You are an intelligent Agentic RAG Assistant with access to multiple tools.
    Your job is to answer user questions by reasoning about which tools to use.

    ## Available Tools:

    1. **search_documents** - Search uploaded documents (PDFs, contracts, reports)
       Use when: Question asks about document content, uploaded files, or internal data

    2. **list_documents** - List all available documents
       Use when: User asks "what documents do I have?" or "which files are indexed?"

    3. **web_search** - Search the internet for current information
       Use when: Question asks about current events, news, public figures, companies, or real-world facts

    ## Decision-Making Guidelines:

    ### When to use ONLY search_documents:
    - "What does my contract say about...?"
    - "Summarize the uploaded report"
    - "What's in my document about...?"

    ### When to use ONLY web_search:
    - "Who is the current CEO of Apple?"
    - "What's the latest news about...?"
    - "What happened in 2026 regarding...?"

    ### When to use BOTH tools (in sequence):
    - "Compare the CEO in my document with Apple's current CEO"
    - "Is the information in my document still accurate?" (search docs first, then verify with web)
    - "How does the policy in my document compare to current industry standards?"

    ## Important Rules:

    1. **Think step-by-step**: Reason about what information you need before acting
    2. **Use tools as needed**: You can call multiple tools in sequence
    3. **Be thorough**: If a question needs both document and web info, use both tools
    4. **Cite sources**: Always mention where information came from
    5. **Chitchat**: For greetings or casual conversation, respond directly without tools
    6. **Uncertainty**: If documents don't have the info, say so clearly

    ## Response Format:

    When you have all the information, provide a clear, comprehensive answer.
    If you used multiple sources, synthesize them intelligently.
""").strip()


class AgenticRAG:

    def __init__(self):
        """Initialize single agentic RAG system with all tools."""
        logger.info("Creating unified Agentic RAG system")

        # Create single agent with all tools
        self.agent = create_agent(
            model=llm,
            tools=[search_documents, list_documents, web_search],
            system_prompt=AGENTIC_RAG_SYSTEM_PROMPT,
        )

        logger.info("Agentic RAG system initialized successfully")

    # --------------------------------------------------
    # MAIN RUN METHOD
    # --------------------------------------------------
    def run(self, query: str, chat_history: list = []) -> dict:
        """
        Execute agentic RAG pipeline.

        The agent will autonomously decide which tools to use based on the query.
        """
        trace = []
        logger.info(f"Processing query: {query}")

        # Step 1: Rewrite query if there's chat history context
        if chat_history:
            chat_context = "\n".join(
                f"{msg['role']}: {msg['content']}"
                for msg in chat_history[-5:]  # Last 5 messages for context
            )
            rewritten_query = rewrite_query(question=query, chat_context=chat_context)
            trace.append(f"Query rewritten: {rewritten_query}")
            logger.info(f"Query rewritten to: {rewritten_query}")
        else:
            rewritten_query = query
            trace.append("No rewriting needed (no chat history)")

        # Step 2: Let the agent handle the query autonomously
        try:
            trace.append("Agent reasoning and selecting tools...")
            logger.info("Invoking agentic RAG system")

            response = self.agent.invoke(
                {"messages": [{"role": "user", "content": rewritten_query}]}
            )

            # Extract the final answer
            raw_answer = extract_agent_answer(response)
            logger.info("Agent completed successfully")

            # Step 3: Parse sources from the response
            sources = self._extract_sources(raw_answer, response)

            # Clean answer (remove source markers if present)
            clean_answer = self._clean_answer(raw_answer)

            # Step 4: Detect which tools were used for trace
            tools_used = self._detect_tools_used(response)
            if tools_used:
                trace.append(f"Tools used: {', '.join(tools_used)}")

            trace.append("Agent completed reasoning and response")

            return {
                "final_answer": clean_answer,
                "sources": sources,
                "route": "agentic",  # Single agentic route
                "trace": trace,
            }

        except Exception as e:
            logger.exception(f"Agentic RAG failed: {str(e)}")
            trace.append(f"Error: {str(e)}")

            return {
                "final_answer": f"I encountered an error processing your question: {str(e)}",
                "sources": [],
                "route": "error",
                "trace": trace,
            }

    # --------------------------------------------------
    # HELPER METHODS
    # --------------------------------------------------

    def _extract_sources(self, raw_answer: str, response: dict) -> list[str]:
        """Extract sources from agent response."""
        sources = []

        # Check for explicit sources section in answer
        if "\n\nSources:\n" in raw_answer:
            _, sources_text = raw_answer.split("\n\nSources:\n", 1)
            sources = [s.strip() for s in sources_text.strip().split("\n") if s.strip()]

        # Also check for URLs in the answer
        for line in raw_answer.split("\n"):
            if line.startswith("URL:"):
                url = line.replace("URL:", "").strip()
                if url and url not in sources:
                    sources.append(url)
            elif "http://" in line or "https://" in line:
                # Extract URLs from text
                words = line.split()
                for word in words:
                    if word.startswith("http"):
                        clean_url = word.strip(".,;:()[]")
                        if clean_url not in sources:
                            sources.append(clean_url)

        return sources

    def _clean_answer(self, raw_answer: str) -> str:
        """Clean the answer by removing source sections."""
        if "\n\nSources:\n" in raw_answer:
            answer, _ = raw_answer.split("\n\nSources:\n", 1)
            return answer.strip()
        return raw_answer.strip()

    def _detect_tools_used(self, response: dict) -> list[str]:
        """Detect which tools were used from agent response."""
        tools_used = []

        # Check response messages for tool calls
        messages = response.get("messages", [])
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.get("name", "")
                    if tool_name and tool_name not in tools_used:
                        tools_used.append(tool_name)

        return tools_used