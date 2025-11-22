"""Test configuration and fixtures."""
import pytest


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return "This is a sample PDF content for testing purposes."


@pytest.fixture
def sample_chunks():
    """Sample chunks for testing."""
    from pdf_agent.domain.pdf.pdf_document import PDFChunk

    return [
        PDFChunk(
            chunk_id="chunk-1",
            content="First chunk content",
            page_number=1,
            chunk_index=0,
            metadata={"page": 1}
        ),
        PDFChunk(
            chunk_id="chunk-2",
            content="Second chunk content",
            page_number=2,
            chunk_index=1,
            metadata={"page": 2}
        )
    ]
