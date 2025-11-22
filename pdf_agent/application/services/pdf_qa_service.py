"""PDF Q&A Service - Application layer service."""

from pdf_agent.application.agent.pdf_qa_agent import PDFQAAgent
from pdf_agent.application.base_service import BaseService
from pdf_agent.application.services.conversation_helper import add_message, create_conversation, get_conversation_history
from pdf_agent.application.services.pdf_document_helper import total_chunks
from pdf_agent.configs.env import LLM_MODEL, LLM_PROVIDER, LLM_TEMPERATURE
from pdf_agent.configs.log import get_logger
from pdf_agent.domain.pdf.conversation import Conversation
from pdf_agent.infrastructure.pdf.pdf_processor import PDFProcessor
from pdf_agent.infrastructure.vectorstore.vector_store import VectorStore

logger = get_logger()


class PDFQAService(BaseService):
    """Service for managing PDF Q&A operations."""

    def __init__(self):
        """Initialize the service with required components."""
        super().__init__()
        self.pdf_processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
        self.vector_store = VectorStore()
        self.agent: PDFQAAgent | None = None
        self.current_conversation: Conversation | None = None
        logger.info(f"PDFQAService initialized with {LLM_PROVIDER} provider")

    def upload_and_index_pdf(self, file_path: str, filename: str) -> dict:
        """
        Upload and index a PDF file.

        Args:
            file_path: Path to the PDF file
            filename: Original filename

        Returns:
            Dict with status and document info
        """
        try:
            logger.info(f"Processing PDF: {filename}")

            # Process PDF
            document = self.pdf_processor.process_pdf(file_path)

            # Index in vector store
            self.vector_store.index_document(document)

            # Initialize agent if not already done
            if not self.agent:
                self.agent = PDFQAAgent(
                    self.vector_store,
                    model_name=LLM_MODEL,
                    temperature=LLM_TEMPERATURE,
                    provider=LLM_PROVIDER
                )

            # Start new conversation
            self.current_conversation = create_conversation(pdf_filename=filename)

            logger.info(f"Successfully indexed {filename} with {total_chunks(document)} chunks")

            return {
                "status": "success",
                "filename": document.filename,
                "total_pages": document.total_pages,
                "total_chunks": total_chunks(document),
                "message": f"PDF '{filename}' successfully uploaded and indexed"
            }

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                "status": "error",
                "message": f"Failed to process PDF: {str(e)}"
            }

    def ask_question(self, question: str) -> dict:
        """
        Ask a question about the PDF.

        Args:
            question: User's question

        Returns:
            Dict with answer and sources
        """
        if not self.agent:
            return {
                "answer": "No PDF has been uploaded yet. Please upload a PDF first.",
                "sources": [],
                "error": "No agent initialized"
            }

        if not self.current_conversation:
            self.current_conversation = create_conversation(
                pdf_filename=self.vector_store.get_current_document_info().get("filename", "Unknown")
            )

        # Add user message to conversation
        add_message(self.current_conversation, "user", question)

        # Get conversation history for context
        history = get_conversation_history(self.current_conversation)[:-1]  # Exclude current question

        # Ask the agent
        result = self.agent.ask(question, conversation_history=history)

        # Add assistant response to conversation
        if "answer" in result:
            add_message(
                self.current_conversation,
                "assistant",
                result["answer"],
                sources=result.get("sources", [])
            )

        return result

    def get_document_info(self) -> dict:
        """Get information about the currently indexed document."""
        return self.vector_store.get_current_document_info()

    def get_conversation_history(self) -> list:
        """Get the current conversation history."""
        if not self.current_conversation:
            return []
        return get_conversation_history(self.current_conversation)

    def clear_conversation(self) -> dict:
        """Clear the current conversation history."""
        if self.current_conversation:
            filename = self.current_conversation.pdf_filename
            self.current_conversation = create_conversation(pdf_filename=filename)
            return {"status": "success", "message": "Conversation cleared"}
        return {"status": "info", "message": "No active conversation"}

    def clear_all(self) -> dict:
        """Clear everything (document, vector store, conversation)."""
        self.vector_store.clear()
        self.current_conversation = None
        self.agent = None
        logger.info("Cleared all data")
        return {"status": "success", "message": "All data cleared"}
