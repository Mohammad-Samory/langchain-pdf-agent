"""Conversation entity - represents a Q&A conversation."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from pdf_agent.domain.shared.base_entity import BaseEntity


@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    sources: Optional[List[dict]] = None  # Page numbers or chunk references


@dataclass
class Conversation(BaseEntity):
    """Conversation aggregate root."""
    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    pdf_filename: str = ""
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, role: str, content: str, sources: Optional[List[dict]] = None):
        """Add a message to the conversation."""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc),
            sources=sources
        )
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)

    def get_conversation_history(self) -> List[dict]:
        """Get formatted conversation history for LangGraph."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in self.messages
        ]
