"""LangGraph React-style agent for PDF Q&A."""
import re
from typing import List, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import SecretStr

from pdf_agent.application.base_service import BaseService
from pdf_agent.configs.env import GOOGLE_API_KEY, LLM_PROVIDER, OPENAI_API_KEY
from pdf_agent.configs.log import get_logger
from pdf_agent.domain.pdf.agent_state import AgentState
from pdf_agent.infrastructure.vectorstore.vector_store import VectorStore

logger = get_logger()


class PDFQAAgent(BaseService):
    """LangGraph-powered conversational agent for PDF Q&A."""

    def __init__(
        self,
        vector_store: VectorStore,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0,
        provider: str | None = None
    ):
        """Initialize the agent with vector store and LLM."""
        super().__init__()
        self.vector_store = vector_store
        self.model_name = model_name
        self.temperature = temperature
        self.provider = provider or LLM_PROVIDER

        # Initialize LLM based on provider
        if self.provider == "google":
            self.llm: ChatOpenAI | ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                api_key=SecretStr(GOOGLE_API_KEY) if GOOGLE_API_KEY else None
            )
            logger.info(f"Initialized PDFQAAgent with Google Gemini: {model_name}")
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=SecretStr(OPENAI_API_KEY) if OPENAI_API_KEY else None
            )
            logger.info(f"Initialized PDFQAAgent with OpenAI: {model_name}")

        # Create the graph
        self.graph = self._create_graph()

    def _create_vector_search_tool(self):
        """Create the vector search tool for LangGraph."""
        @tool
        def search_pdf(query: str, k: int = 4) -> str:
            """
            Search the PDF document for relevant information.
            Use this tool when you need to find specific information from the PDF.

            Args:
                query: The search query (natural language)
                k: Number of results to return (default: 4)

            Returns:
                Formatted search results with page numbers and excerpts
            """
            logger.info(f"Tool called: search_pdf(query='{query}', k={k})")

            results = self.vector_store.similarity_search(query, k=k)

            if not results:
                return "No relevant information found in the PDF."

            # Format results
            formatted_results = []
            for idx, (doc, score) in enumerate(results, 1):
                page_num = doc.metadata.get("page_number", "Unknown")
                content = doc.page_content[:300]  # Limit content length

                formatted_results.append(
                    f"Result {idx} (Page {page_num}, Score: {score:.3f}):\n{content}..."
                )

            return "\n\n".join(formatted_results)

        return search_pdf

    def _create_graph(self):
        """Create the LangGraph workflow."""
        # Create tool
        search_tool = self._create_vector_search_tool()
        tools = [search_tool]

        # Bind tools to LLM
        llm_with_tools = self.llm.bind_tools(tools)

        # Define workflow
        workflow = StateGraph(AgentState)

        # Define nodes
        def agent_node(state: AgentState):
            """Agent reasoning node."""
            logger.info("Agent node: Reasoning about the question")
            messages = state["messages"]
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}

        def tool_node(state: AgentState):
            """Tool execution node."""
            logger.info("Tool node: Executing vector search")
            # Execute tools
            tool_executor = ToolNode(tools)
            result = tool_executor.invoke(state)

            return result

        def should_continue(state: AgentState) -> Literal["tools", "end"]:
            """Decide whether to continue or end."""
            messages = state["messages"]
            last_message = messages[-1]

            # If there are tool calls, continue to tools
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                logger.info("Decision: Continue to tools")
                return "tools"

            # Otherwise, end
            logger.info("Decision: End conversation")
            return "end"

        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)

        # Set entry point
        workflow.set_entry_point("agent")

        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )

        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")

        # Compile
        return workflow.compile()

    def ask(self, question: str, conversation_history: List[dict] | None = None) -> dict:
        """
        Ask a question about the PDF.

        Args:
            question: User's question
            conversation_history: Previous messages (optional)

        Returns:
            Dict with answer and sources
        """
        logger.info(f"Received question: '{question}'")

        # Check if document is loaded
        doc_info = self.vector_store.get_current_document_info()
        if "status" in doc_info and doc_info["status"] == "No document indexed":
            return {
                "answer": "No PDF document is currently loaded. Please upload a PDF first.",
                "sources": [],
                "error": "No document indexed"
            }

        # Prepare system message
        system_message = SystemMessage(
            content=f"""You are a helpful assistant that answers questions about a PDF document.
The document is: {doc_info['filename']} ({doc_info['total_pages']} pages).

When answering:
1. Use the search_pdf tool to find relevant information from the document
2. Always cite page numbers when referencing information
3. If the information is not in the document, say so clearly
4. Provide concise, accurate answers based on the document content

Be conversational and helpful."""
        )

        # Build messages
        messages: list[BaseMessage] = [system_message]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # Add current question
        messages.append(HumanMessage(content=question))

        # Invoke the graph
        try:
            result = self.graph.invoke({"messages": messages})  # type: ignore[attr-defined]

            # Extract final answer
            final_message = result["messages"][-1]
            answer = final_message.content

            # Extract sources (page numbers mentioned)
            sources = self._extract_sources(result["messages"])

            logger.info(f"Generated answer with {len(sources)} sources")

            return {
                "answer": answer,
                "sources": sources,
                "conversation": result["messages"]
            }

        except Exception as e:
            logger.error(f"Error during agent execution: {e}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "sources": [],
                "error": str(e)
            }

    def _extract_sources(self, messages: List[BaseMessage]) -> List[dict]:
        """Extract page numbers and sources from messages."""
        sources = []

        for msg in messages:
            content = str(msg.content)

            # Look for page numbers in the format "Page X"
            page_matches = re.findall(r'Page (\d+)', content)

            for page_num in set(page_matches):
                sources.append({
                    "page": int(page_num),
                    "type": "reference"
                })

        return sources
