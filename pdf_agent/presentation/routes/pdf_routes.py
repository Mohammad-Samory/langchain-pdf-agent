"""API routes for PDF Q&A."""
import os
import tempfile
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from pdf_agent.application.services.pdf_qa_service import PDFQAService
from pdf_agent.configs.log import get_logger

logger = get_logger()
router = APIRouter()

# Singleton service instance
_pdf_qa_service: Optional[PDFQAService] = None


def get_pdf_qa_service() -> PDFQAService:
    """Get or create the PDF Q&A service singleton."""
    global _pdf_qa_service
    if _pdf_qa_service is None:
        _pdf_qa_service = PDFQAService()
        logger.info("Created new PDFQAService singleton instance")
    return _pdf_qa_service


class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(..., description="Question about the PDF", min_length=1)


class AnswerResponse(BaseModel):
    """Response model for answers."""
    answer: str
    sources: List[dict] = []
    error: Optional[str] = None


class DocumentInfo(BaseModel):
    """Response model for document information."""
    filename: Optional[str] = None
    total_pages: Optional[int] = None
    total_chunks: Optional[int] = None
    upload_date: Optional[str] = None
    status: Optional[str] = None


@router.post("/upload", summary="Upload a PDF file")
async def upload_pdf(file: UploadFile = File(...), service: PDFQAService = Depends(get_pdf_qa_service)) -> dict:
    """
    Upload and index a PDF file for Q&A.

    - **file**: PDF file to upload

    Returns document information and indexing status.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    logger.info(f"Received PDF upload: {file.filename}")

    # Save to temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Process and index
        result = service.upload_and_index_pdf(tmp_path, file.filename)

        # Clean up temp file
        os.unlink(tmp_path)

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))

        return result

    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        # Clean up temp file if it exists
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AnswerResponse, summary="Ask a question")
async def ask_question(request: QuestionRequest, service: PDFQAService = Depends(get_pdf_qa_service)) -> AnswerResponse:
    """
    Ask a question about the uploaded PDF.

    - **question**: Natural language question about the document

    Returns an answer grounded in the PDF content with source citations.
    """
    logger.info(f"Received question: {request.question}")

    try:
        result = service.ask_question(request.question)

        return AnswerResponse(
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document", response_model=DocumentInfo, summary="Get document info")
async def get_document_info(service: PDFQAService = Depends(get_pdf_qa_service)) -> DocumentInfo:
    """
    Get information about the currently indexed document.

    Returns document metadata including filename, page count, and chunk count.
    """
    info = service.get_document_info()
    return DocumentInfo(**info)


@router.get("/conversation", summary="Get conversation history")
async def get_conversation(service: PDFQAService = Depends(get_pdf_qa_service)) -> dict:
    """
    Get the conversation history for the current session.

    Returns list of messages with timestamps.
    """
    history = service.get_conversation_history()
    return {
        "conversation": history,
        "message_count": len(history)
    }


@router.delete("/conversation", summary="Clear conversation")
async def clear_conversation(service: PDFQAService = Depends(get_pdf_qa_service)) -> dict:
    """
    Clear the current conversation history.

    Keeps the indexed document but resets the conversation.
    """
    return service.clear_conversation()


@router.delete("/all", summary="Clear everything")
async def clear_all(service: PDFQAService = Depends(get_pdf_qa_service)) -> dict:
    """
    Clear the indexed document and conversation.

    Resets the service to initial state.
    """
    return service.clear_all()
