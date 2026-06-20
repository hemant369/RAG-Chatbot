from textwrap import dedent
from langchain_classic.agents import AgentExecutor
from langchain_classic.agents import create_react_agent
from langchain_core.prompts import PromptTemplate
from app.agents.tools import search_documents, list_documents, web_search
from app.utils.query_rewriter import rewrite_query
from app.utils.agent_extract import extract_agent_answer
from app.utils.logger import logger
from app.models.llm import chat_llm as llm


# ReAct prompt template for explicit tool usage
REACT_PROMPT_TEMPLATE = """You are a RAG Assistant. All knowledge about documents comes exclusively from tools — never from your own memory or training data.

    Available tools:
    {tools}

    Tool names: {tool_names}

    ---

    ROUTING RULES (follow exactly):
    1. Question mentions a document, PDF, file, or specific content → use search_documents
    2. Question asks "what files/documents do I have?" or similar → use list_documents
    3. Question is about current events, recent news, or public facts → use web_search
    4. Question is ONLY a greeting (hi, hello, hey) → skip tools, go to Final Answer directly

    ---

    Use this format EXACTLY — do not skip or reorder any line:

    Question: the input question you must answer
    Thought: think about which rule above applies and which tool to use
    Action: the tool to use, must be one of [{tool_names}]
    Action Input: a short, specific search phrase (keywords only, no questions)
    Observation: the result returned by the tool
    Thought: I now have enough information to answer
    Final Answer: a clear answer based only on the Observation above

    If you need more information after the first Observation, repeat:
    Thought / Action / Action Input / Observation
    before writing your Final Answer.

    If the Observation returns no results, write:
    Final Answer: I couldn't find any information about that in your documents.

    ---

    EXAMPLES:

    Question: What are the termination clauses?
    Thought: This asks about specific content inside a document. Rule 1 applies — I must use search_documents.
    Action: search_documents
    Action Input: termination clauses contract 2024
    Observation: "Section 8.2 — Either party may terminate this agreement with 30 days written notice. Immediate termination is permitted in cases of material breach."
    Thought: I now have the termination clause details.
    Final Answer: According to contract_2024.pdf, either party may terminate the agreement with 30 days written notice. Immediate termination is allowed in cases of material breach (Section 8.2).

    ---

    Question: What files do I have?
    Thought: The user is asking what documents are available. Rule 2 applies — I must use list_documents.
    Action: list_documents
    Action Input: list all
    Observation: Found 3 documents: contract_2024.pdf, legal_terms.pdf, property_agreement.pdf
    Thought: I now have the list of documents.
    Final Answer: You have 3 documents: contract_2024.pdf, legal_terms.pdf, and property_agreement.pdf.

    ---

    Question: What happened in the 2024 US election?
    Thought: This is about a public news event. Rule 3 applies — I must use web_search.
    Action: web_search
    Action Input: 2024 US election results
    Observation: Donald Trump won the 2024 US presidential election, defeating Kamala Harris with 312 electoral votes.
    Thought: I now have the answer from the web.
    Final Answer: Donald Trump won the 2024 US presidential election, defeating Kamala Harris with 312 electoral votes.

    ---

    Question: Hello!
    Thought: This is only a greeting. Rule 4 applies — no tools needed.
    Final Answer: Hello! How can I help you with your documents today?

    ---

    Begin!

    Question: {input}
    Thought: {agent_scratchpad}"""


class AgenticRAG:

    def __init__(self):
        """Initialize single agentic RAG system with all tools."""
        # Define tools
        self.tools = [search_documents, list_documents, web_search]

        # Create ReAct prompt
        prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)

        # Create ReAct agent
        agent = create_react_agent(
            llm=llm,
            tools=self.tools,
            prompt=prompt,
        )

        # Create agent executor
        self.agent = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True,
        )

    # --------------------------------------------------
    # MAIN RUN METHOD
    # --------------------------------------------------
    def run(self, query: str, chat_history: list = []) -> dict:
        """
        Execute agentic RAG pipeline.
        The agent will autonomously decide which tools to use based on the query.
        """
        trace = []

        # Step 1: Rewrite query if there's chat history context
        if chat_history:
            chat_context = "\n".join(
                f"{msg['role']}: {msg['content']}"
                for msg in chat_history[-5:]
            )
            rewritten_query = rewrite_query(question=query, chat_context=chat_context)
            trace.append(f"Query rewritten: {rewritten_query}")
        else:
            rewritten_query = query

        # Step 2: Let the agent handle the query autonomously
        try:
            trace.append("Agent reasoning and selecting tools...")

            # ReAct agent expects {"input": query} format
            response = self.agent.invoke({"input": rewritten_query})

            # Extract the final answer from ReAct agent response
            raw_answer = response.get("output", "No response generated")

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
                "tool_calls": tools_used,
                "intermediate_steps": response.get("intermediate_steps", []),
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