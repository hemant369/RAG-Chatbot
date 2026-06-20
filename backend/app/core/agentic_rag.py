from textwrap import dedent
from langchain_classic.agents import AgentExecutor
from langchain_classic.agents import create_react_agent
from langchain_core.prompts import PromptTemplate
from app.agents.tools import search_documents, list_documents, web_search
from app.utils.query_rewriter import rewrite_query
from app.utils.agent_extract import extract_agent_answer
from app.utils.logger import logger, is_main_process
from app.models.llm import chat_llm as llm


# ReAct prompt template for explicit tool usage
REACT_PROMPT_TEMPLATE = """You are an intelligent RAG Assistant. Answer the question using the available tools.

CRITICAL RULE: You have NO access to document content. You MUST use tools to get information.

Available tools:
{tools}

Tool names: {tool_names}

Use this format EXACTLY:

Question: the input question you must answer
Thought: think about what information you need
Action: the tool to use, must be one of [{tool_names}]
Action Input: the input to the tool
Observation: the result from the tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the original question

MANDATORY RULES:
1. For ANY question about documents, PDFs, files, or specific content → use search_documents
2. For questions about current events, news, public info → use web_search
3. For "what documents do I have?" → use list_documents
4. For greetings only → skip tools and go straight to Final Answer

Examples:

Question: Tell me about comparison deeds
Thought: This is asking about document content, I must use search_documents
Action: search_documents
Action Input: comparison deeds
Observation: [results from tool]
Thought: I now have the information from the documents
Final Answer: [answer based on observation]

Question: What are the key points in legal.pdf?
Thought: This explicitly asks about a document, I must search it
Action: search_documents
Action Input: key points legal
Observation: [results from tool]
Thought: I now have the key points from the document
Final Answer: [answer based on observation]

Question: Hello
Thought: This is just a greeting, no tools needed
Final Answer: Hello! How can I help you with your documents today?

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


class AgenticRAG:

    def __init__(self):
        """Initialize single agentic RAG system with all tools."""
        if is_main_process():
            logger.info("Creating unified Agentic RAG system (ReAct)")

        # Define tools
        self.tools = [search_documents, list_documents, web_search]

        # Create ReAct prompt
        prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)

        # Create ReAct agent (better for smaller models)
        agent = create_react_agent(
            llm=llm,
            tools=self.tools,
            prompt=prompt,
        )

        # Create agent executor
        self.agent = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # Enable verbose for debugging
            handle_parsing_errors=True,  # Handle parsing errors gracefully
            max_iterations=5,  # Limit iterations
        )

        if is_main_process():
            logger.info("Agentic RAG system initialized successfully (ReAct)")

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
            logger.info("Invoking agentic RAG system (ReAct)")

            # ReAct agent expects {"input": query} format
            response = self.agent.invoke({"input": rewritten_query})

            # Extract the final answer from ReAct agent response
            raw_answer = response.get("output", "No response generated")
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

        # Check for intermediate steps in ReAct agent response
        intermediate_steps = response.get("intermediate_steps", [])
        for step in intermediate_steps:
            if len(step) >= 1:
                action = step[0]
                if hasattr(action, "tool"):
                    tool_name = action.tool
                    if tool_name and tool_name not in tools_used:
                        tools_used.append(tool_name)

        return tools_used