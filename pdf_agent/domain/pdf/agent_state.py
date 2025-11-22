"""Agent state entity for PDF Q&A agent."""
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the PDF Q&A agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    search_results: list[dict]
    final_answer: str
