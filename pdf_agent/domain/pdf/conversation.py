"""Conversation entity - represents a Q&A conversation."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pdf_agent.domain.shared.base_entity import BaseEntity


@dataclass
class Message:
    """A single message in the conversation."""
    role: str
    content: str
    timestamp: datetime
    sources: list[dict[str, Any]] | None = None


@dataclass
class Conversation(BaseEntity):
    """Conversation aggregate root."""
    pdf_filename: str
    messages: list[Message] | None = None
