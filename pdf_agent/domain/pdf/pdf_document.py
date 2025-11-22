"""PDF Document entity - represents a PDF in the domain."""
from dataclasses import dataclass
from datetime import datetime

from pdf_agent.domain.shared.base_entity import BaseEntity


@dataclass
class PDFChunk:
    """Represents a chunk of text from a PDF with metadata."""
    chunk_id: str
    content: str
    page_number: int
    chunk_index: int
    metadata: dict


@dataclass
class PDFDocument(BaseEntity):
    """PDF Document aggregate root."""
    filename: str
    file_path: str
    total_pages: int
    file_size: int
    upload_date: datetime
    chunks: list[PDFChunk] | None = None
