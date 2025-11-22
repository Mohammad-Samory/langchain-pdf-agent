"""Tests for PDF Q&A service."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from pdf_agent.domain.pdf.pdf_document import PDFChunk, PDFDocument


class TestPDFDocument:
    """Tests for PDFDocument entity."""

    def test_pdf_document_creation(self):
        """Test creating a PDF document."""
        chunks = [
            PDFChunk(
                chunk_id="1",
                content="Test content",
                page_number=1,
                chunk_index=0,
                metadata={"page": 1}
            )
        ]

        now = datetime.now(timezone.utc)
        doc = PDFDocument(
            id=uuid4(),
            filename="test.pdf",
            file_path="/path/to/test.pdf",
            total_pages=1,
            file_size=1024,
            upload_date=now,
            created_at=now,
            updated_at=now,
            chunks=chunks
        )

        assert doc.filename == "test.pdf"
        assert doc.total_chunks() == 1
        assert len(doc.get_chunks_for_pages([1])) == 1


class TestPDFQAService:
    """Tests for PDF Q&A Service."""

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initializes correctly."""
        from pdf_agent.application.services.pdf_qa_service import PDFQAService

        service = PDFQAService()

        assert service.pdf_processor is not None
        assert service.vector_store is not None
        assert service.agent is None  # Not initialized until PDF upload


# Add more tests as needed
