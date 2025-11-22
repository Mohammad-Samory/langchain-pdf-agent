"""Helper functions for Conversation domain operations."""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4, UUID

from pdf_agent.domain.pdf.conversation import Conversation, Message


def create_conversation(pdf_filename: str) -> Conversation:
    """Create a new conversation instance with default values."""
    now = datetime.now(timezone.utc)
    return Conversation(
        id=uuid4(),
        created_at=now,
        updated_at=now,
        pdf_filename=pdf_filename,
        messages=[]
    )


def add_message(conversation: Conversation, role: str, content: str, sources: Optional[List[dict]] = None) -> None:
    """Add a message to the conversation."""
    message = Message(
        role=role,
        content=content,
        timestamp=datetime.now(timezone.utc),
        sources=sources
    )
    conversation.messages.append(message)
    conversation.updated_at = datetime.now(timezone.utc)


def get_conversation_history(conversation: Conversation) -> List[dict]:
    """Get formatted conversation history for LangGraph."""
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in conversation.messages
    ]
