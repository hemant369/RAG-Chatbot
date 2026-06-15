from textwrap import dedent
from langchain_ollama import ChatOllama
from app.agents.rag_agent import get_rag_agent
from app.agents.web_agent import get_web_agent
from app.agents.comparison_agent import compare_answers
from app.utils.query_rewriter import rewrite_query
from app.utils.agent_extract import extract_agent_answer
from app.utils.logger import logger


llm = ChatOllama(model="qwen2.5:3b", temperature=0)


class AgenticRAG:

    def __init__(self):
        self.rag_agent = get_rag_agent()
        self.web_agent = get_web_agent()

    # --------------------------------------------------
    # SUPERVISOR
    # --------------------------------------------------
    def supervisor(self, query: str) -> str:
        prompt = dedent(f"""
            You are a routing agent. Read the question carefully.

            Return "web" if the question asks about:
            - People (CEOs, founders, politicians)
            - Current events or news
            - Companies and their status
            - Any real world facts not in a document

            Return "rag" if the question asks about:
            - Uploaded documents, PDFs, contracts, reports

            Return "compare" if the question needs BOTH documents AND web.
            Return "chitchat" for greetings or casual conversation.

            Question: {query}

            You MUST reply with EXACTLY one of these four words, nothing else:
            rag | web | compare | chitchat
        """).strip()

        response = llm.invoke(prompt)
        route = response.content.strip().lower()

        VALID_ROUTES = {"rag", "web", "compare", "chitchat"}

        # Ask LLM to self-correct if invalid
        if route not in VALID_ROUTES:
            correction_prompt = f"""
            You replied "{route}" but I need EXACTLY one of: rag, web, compare, chitchat
            No explanation. No extra words. Just the single word.
            """
            route = llm.invoke(correction_prompt).content.strip().lower()

        # Final hard fallback
        if route not in VALID_ROUTES:
            logger.warning(f"Supervisor failed twice, defaulting to 'rag'")
            route = "rag"

        logger.info(f"Supervisor selected route: {route}")
        return route

    # --------------------------------------------------
    # RAG
    # --------------------------------------------------
    def run_rag(self, query: str) -> tuple[str, list[str]]:
        logger.info("Executing RAG Agent")

        response = self.rag_agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )

        raw_answer = extract_agent_answer(response)

        if "\n\nSources:\n" in raw_answer:
            answer, sources_text = raw_answer.split("\n\nSources:\n", 1)
            sources = [s.strip() for s in sources_text.strip().split("\n") if s.strip()]
        else:
            answer = raw_answer
            sources = []

        logger.info("RAG Agent completed")
        return answer, sources

    # --------------------------------------------------
    # WEB
    # --------------------------------------------------
    def run_web(self, query: str) -> tuple[str, list[str]]:
        logger.info("Executing Web Agent")

        response = self.web_agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )

        raw_answer = extract_agent_answer(response)

        # extract URLs
        sources = []
        for line in raw_answer.split("\n"):
            if line.startswith("URL:"):
                url = line.replace("URL:", "").strip()
                if url:
                    sources.append(url)

        # summarize raw web results
        summary_prompt = f"""
        Based on these web search results, provide a clean concise answer to: {query}
        Results: {raw_answer}
        Answer only, no URLs or titles.
        """
        clean_answer = llm.invoke(summary_prompt).content.strip()

        logger.info("Web Agent completed")
        return clean_answer, sources


    # --------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------
    def run(self, query: str, chat_history: list = []) -> dict:
        trace = []

        # Step 1 - supervisor decides FIRST on original query
        route = self.supervisor(query)
        trace.append(f"Supervisor selected: {route}")

        sources = []

        # Step 2 - only rewrite if it's a real query
        if route == "chitchat":
            answer = llm.invoke(query).content.strip()
            trace.append("Chitchat handled, no rewrite needed")

        else:
            # Rewrite only for rag/web/compare
            chat_context = "\n".join(
                f"{msg['role']}: {msg['content']}"
                for msg in chat_history
            )
            rewritten = rewrite_query(question=query, chat_context=chat_context)
            trace.append(f"Query rewritten: {rewritten}")

            if route == "rag":
                answer, sources = self.run_rag(rewritten)
                trace.append("RAG agent executed")

            elif route == "web":
                answer, sources = self.run_web(rewritten)
                trace.append("Web agent executed")

            elif route == "compare":
                rag_answer, rag_sources = self.run_rag(rewritten)
                trace.append("RAG agent executed")

                web_answer, web_sources = self.run_web(rewritten)
                trace.append("Web agent executed")

                answer = compare_answers(rewritten, rag_answer, web_answer)
                sources = rag_sources + web_sources
                trace.append("Comparison agent executed")

            else:
                answer = "No response generated"

        return {
            "final_answer": answer,
            "sources": sources,
            "route": route,
            "trace": trace,
        }