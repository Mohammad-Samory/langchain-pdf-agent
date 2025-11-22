"""In-memory vector store using FAISS and sentence transformers."""
from typing import List, Optional, Tuple

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from pdf_agent.application.services.pdf_document_helper import total_chunks
from pdf_agent.configs.log import get_logger
from pdf_agent.domain.pdf.pdf_document import PDFDocument

logger = get_logger()


class VectorStore:
    """In-memory vector store for PDF chunks using FAISS."""

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize vector store with embedding model."""
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store: Optional[FAISS] = None
        self.current_document: Optional[PDFDocument] = None
        logger.info(f"Initialized VectorStore with model: {embedding_model}")

    def index_document(self, document: PDFDocument) -> None:
        """Index a PDF document's chunks into the vector store."""
        if document.chunks is None:
            logger.warning(f"Document {document.filename} has no chunks")
            return

        logger.info(f"Indexing document: {document.filename} with {len(document.chunks)} chunks")

        # Convert chunks to LangChain Document format
        documents = []
        for chunk in document.chunks:
            doc = Document(
                page_content=chunk.content,
                metadata={
                    "chunk_id": chunk.chunk_id,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "filename": document.filename,
                    **chunk.metadata
                }
            )
            documents.append(doc)

        # Create FAISS index
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        self.current_document = document
        logger.info(f"Successfully indexed {len(documents)} chunks")

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        score_threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """
        Perform similarity search on the indexed document.

        Args:
            query: Natural language query
            k: Number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of (Document, score) tuples
        """
        if not self.vector_store:
            logger.warning("No document indexed in vector store")
            return []

        logger.info(f"Searching for: '{query}' (top {k} results)")

        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(query, k=k)

        # Filter by score threshold if needed
        filtered_results = [
            (doc, score) for doc, score in results
            if score >= score_threshold
        ]

        logger.info(f"Found {len(filtered_results)} results above threshold {score_threshold}")

        return filtered_results

    def get_current_document_info(self) -> dict:
        """Get information about the currently indexed document."""
        if not self.current_document:
            return {"status": "No document indexed"}

        return {
            "filename": self.current_document.filename,
            "total_pages": self.current_document.total_pages,
            "total_chunks": total_chunks(self.current_document),
            "upload_date": self.current_document.upload_date.isoformat()
        }

    def clear(self) -> None:
        """Clear the vector store."""
        self.vector_store = None
        self.current_document = None
        logger.info("Vector store cleared")
