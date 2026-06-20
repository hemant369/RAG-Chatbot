from textwrap import dedent
from langchain.agents import create_agent
from app.agents.tools import search_documents, list_documents, web_search
from app.utils.query_rewriter import rewrite_query
from app.utils.agent_extract import extract_agent_answer
from app.utils.logger import logger
from app.models.llm import chat_llm as llm


# Comprehensive system prompt for single agentic RAG system
AGENTIC_RAG_SYSTEM_PROMPT = dedent("""
    You are an intelligent Agentic RAG Assistant with access to tools.

    ## CRITICAL: You Have NO Knowledge of User Documents

    You do NOT have access to any document content in your knowledge base.
    You MUST use the search_documents tool for ANY question about documents.
    NEVER guess or make assumptions about document content.

    ## Available Tools:

    1. **search_documents** - Search uploaded documents (PDFs, contracts, reports)
    2. **list_documents** - List all available documents
    3. **web_search** - Search the internet for current information

    ## MANDATORY Tool Usage Rules:

    ### ALWAYS use search_documents for these queries:
    - ANY question about document content ("what does my document say...")
    - Document summaries ("summarize the report...")
    - Specific information from files ("tell me about X in the document...")
    - Questions mentioning: "document", "PDF", "file", "uploaded", "contract", "report"
    - Questions about specific topics that could be in documents ("comparison deeds", "legal terms", etc.)

    ### ALWAYS use web_search for these queries:
    - Current events and news ("what happened today...")
    - Public figures ("who is the CEO of...")
    - Real-time information ("latest news about...")
    - Public company/technology information

    ### Use BOTH tools in sequence for:
    - Comparison queries ("compare document info with current data...")
    - Verification queries ("is my document info still accurate...")

    ### Respond directly (no tools) ONLY for:
    - Greetings: "hello", "hi", "how are you"
    - General chat: "thank you", "goodbye"

    ## Step-by-Step Process:

    1. **Analyze the query**: Does it mention documents, files, or specific content?
    2. **If YES**: IMMEDIATELY use search_documents tool - do NOT respond directly
    3. **If NO**: Check if it needs web info or is just chitchat
    4. **Wait for tool results**: Never answer before calling the appropriate tool
    5. **Synthesize response**: Use the tool's output to formulate your answer

    ## Examples:

    User: "Tell me about comparison deeds"
    → Think: This could be in a document
    → Action: Call search_documents("comparison deeds")
    → Wait for results, then respond

    User: "What are the key points in legal.pdf?"
    → Think: Explicitly asking about a document
    → Action: Call search_documents("key points legal")
    → Wait for results, then respond

    User: "Who is the CEO of Microsoft?"
    → Think: Public information, not document-related
    → Action: Call web_search("CEO Microsoft")
    → Wait for results, then respond

    User: "Hello"
    → Think: Greeting, no tools needed
    → Action: Respond directly with friendly greeting

    ## Error Handling:

    If search_documents returns no results:
    - Do NOT say "please upload the document"
    - Instead say: "I couldn't find information about [topic] in the indexed documents. The document may not contain this information, or it may not be indexed yet."

    ## Remember:

    - You have ZERO knowledge of document content
    - ALWAYS use search_documents for document questions
    - NEVER make up document information
    - Tool results are your ONLY source of document information
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