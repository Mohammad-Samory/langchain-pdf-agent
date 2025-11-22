"""API routes for PDF Q&A."""
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pdf_agent.presentation.dependencies import get_service
from pdf_agent.application.services.pdf_qa_service import PDFQAService
from pdf_agent.configs.log import get_logger
from pdf_agent.presentation.models.pdf_models import (
    AskQuestionRequest,
    AskQuestionResponse,
    ClearAllResponse,
    ClearConversationResponse,
    GetConversationResponse,
    GetDocumentInfoResponse,
    UploadPDFResponse,
)

logger = get_logger()
router = APIRouter()


@router.post("/upload", response_model=UploadPDFResponse, summary="Upload a PDF file")
async def upload_pdf(file: UploadFile = File(...), service: PDFQAService = Depends(get_service(PDFQAService))) -> UploadPDFResponse:
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

        return UploadPDFResponse(**result)

    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        # Clean up temp file if it exists
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AskQuestionResponse, summary="Ask a question")
async def ask_question(request: AskQuestionRequest, service: PDFQAService = Depends(get_service(PDFQAService))) -> AskQuestionResponse:
    """
    Ask a question about the uploaded PDF.

    - **question**: Natural language question about the document

    Returns an answer grounded in the PDF content with source citations.
    """
    logger.info(f"Received question: {request.question}")

    try:
        result = service.ask_question(request.question)

        return AskQuestionResponse(
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document", response_model=GetDocumentInfoResponse, summary="Get document info")
async def get_document_info(service: PDFQAService = Depends(get_service(PDFQAService))) -> GetDocumentInfoResponse:
    """
    Get information about the currently indexed document.

    Returns document metadata including filename, page count, and chunk count.
    """
    info = service.get_document_info()
    return GetDocumentInfoResponse(**info)


@router.get("/conversation", response_model=GetConversationResponse, summary="Get conversation history")
async def get_conversation(service: PDFQAService = Depends(get_service(PDFQAService))) -> GetConversationResponse:
    """
    Get the conversation history for the current session.

    Returns list of messages with timestamps.
    """
    history = service.get_conversation_history()
    return GetConversationResponse(
        conversation=history,
        message_count=len(history)
    )


@router.delete("/conversation", response_model=ClearConversationResponse, summary="Clear conversation")
async def clear_conversation(service: PDFQAService = Depends(get_service(PDFQAService))) -> ClearConversationResponse:
    """
    Clear the current conversation history.

    Keeps the indexed document but resets the conversation.
    """
    result = service.clear_conversation()
    return ClearConversationResponse(**result)


@router.delete("/all", response_model=ClearAllResponse, summary="Clear everything")
async def clear_all(service: PDFQAService = Depends(get_service(PDFQAService))) -> ClearAllResponse:
    """
    Clear the indexed document and conversation.

    Resets the service to initial state.
    """
    result = service.clear_all()
    return ClearAllResponse(**result)
