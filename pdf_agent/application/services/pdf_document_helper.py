"""Helper functions for PDFDocument domain operations."""
from typing import List

from pdf_agent.domain.pdf.pdf_document import PDFDocument, PDFChunk


def get_chunks_for_pages(document: PDFDocument, pages: List[int]) -> List[PDFChunk]:
    """Get all chunks for specific pages."""
    if not document.chunks:
        return []
    return [chunk for chunk in document.chunks if chunk.page_number in pages]


def total_chunks(document: PDFDocument) -> int:
    """Get total number of chunks."""
    if not document.chunks:
        return 0
    return len(document.chunks)
