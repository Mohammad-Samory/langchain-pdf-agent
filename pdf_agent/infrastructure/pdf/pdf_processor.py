"""PDF processor - extracts text and chunks from PDF files."""
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from uuid import UUID

import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter

from pdf_agent.domain.pdf.pdf_document import PDFChunk, PDFDocument


class PDFProcessor:
    """Handles PDF text extraction and chunking."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def extract_text_from_pdf(self, pdf_path: str) -> List[tuple[str, int]]:
        """
        Extract text from PDF with page numbers.
        Returns: List of (text, page_number) tuples.
        """
        text_with_pages = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    text_with_pages.append((text, page_num))

        return text_with_pages

    def chunk_text(self, text_with_pages: List[tuple[str, int]]) -> List[PDFChunk]:
        """
        Chunk the extracted text while preserving page numbers.
        """
        chunks = []
        chunk_counter = 0

        for text, page_num in text_with_pages:
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(text)

            for chunk_text in text_chunks:
                chunk_id = hashlib.md5(
                    f"{page_num}_{chunk_counter}_{chunk_text[:50]}".encode()
                ).hexdigest()

                chunk = PDFChunk(
                    chunk_id=chunk_id,
                    content=chunk_text,
                    page_number=page_num,
                    chunk_index=chunk_counter,
                    metadata={
                        "page": page_num,
                        "chunk_index": chunk_counter,
                        "char_count": len(chunk_text)
                    }
                )
                chunks.append(chunk)
                chunk_counter += 1

        return chunks

    def process_pdf(self, pdf_path: str) -> PDFDocument:
        """
        Process a PDF file end-to-end.
        Returns: PDFDocument entity with all chunks.
        """
        path = Path(pdf_path)

        # Extract text with page numbers
        text_with_pages = self.extract_text_from_pdf(pdf_path)

        # Chunk the text
        chunks = self.chunk_text(text_with_pages)

        # Create PDFDocument entity
        now = datetime.now(timezone.utc)
        doc_id_str = hashlib.md5(path.name.encode()).hexdigest()
        document = PDFDocument(
            id=UUID(doc_id_str[:32].ljust(32, '0')),
            filename=path.name,
            file_path=str(path.absolute()),
            total_pages=len(text_with_pages),
            chunks=chunks,
            upload_date=now,
            file_size=path.stat().st_size,
            created_at=now,
            updated_at=now
        )

        return document
