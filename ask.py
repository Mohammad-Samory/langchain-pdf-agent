"""CLI script for PDF Q&A agent.

Usage:
    python ask.py --upload document.pdf
    python ask.py --question "What is the main topic?"
    python ask.py -q "Summarize the findings" --verbose
"""
import argparse
import sys
from pathlib import Path

from pdf_agent.application.services.pdf_qa_service import PDFQAService
from pdf_agent.configs.log import get_logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

logger = get_logger()


def main():
    parser = argparse.ArgumentParser(
        description="PDF Q&A Agent - Ask questions about PDF documents"
    )

    parser.add_argument(
        "--upload",
        type=str,
        help="Path to PDF file to upload and index"
    )

    parser.add_argument(
        "-q", "--question",
        type=str,
        help="Question to ask about the PDF"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show information about the currently indexed document"
    )

    parser.add_argument(
        "--history",
        action="store_true",
        help="Show conversation history"
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the current conversation"
    )

    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear everything (document and conversation)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Initialize service
    service = PDFQAService()

    # Handle upload
    if args.upload:
        pdf_path = Path(args.upload)
        if not pdf_path.exists():
            print(f"❌ Error: File not found: {pdf_path}")
            sys.exit(1)

        if not pdf_path.suffix.lower() == '.pdf':
            print("❌ Error: File must be a PDF")
            sys.exit(1)

        print(f"📄 Uploading and indexing: {pdf_path.name}")
        result = service.upload_and_index_pdf(str(pdf_path), pdf_path.name)

        if result.get("status") == "success":
            print(f"✅ {result['message']}")
            print(f"   📊 Pages: {result['total_pages']}")
            print(f"   🔢 Chunks: {result['total_chunks']}")
        else:
            print(f"❌ Error: {result.get('message')}")
            sys.exit(1)

    # Handle info
    if args.info:
        info = service.get_document_info()
        if "status" in info and info["status"] == "No document indexed":
            print("ℹ️  No document currently indexed")
        else:
            print(f"📄 Current Document: {info['filename']}")
            print(f"   📊 Pages: {info['total_pages']}")
            print(f"   🔢 Chunks: {info['total_chunks']}")
            print(f"   📅 Uploaded: {info['upload_date']}")

    # Handle question
    if args.question:
        print(f"\n❓ Question: {args.question}\n")

        result = service.ask_question(args.question)

        if "error" in result and result["error"]:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)

        print(f"💬 Answer:\n{result['answer']}\n")

        if result.get("sources"):
            print("📚 Sources:")
            for source in result["sources"]:
                print(f"   - Page {source['page']}")

        if args.verbose and "conversation" in result:
            print(f"\n🔍 Conversation turns: {len(result['conversation'])}")

    # Handle history
    if args.history:
        history = service.get_conversation_history()
        if not history:
            print("ℹ️  No conversation history")
        else:
            print(f"📜 Conversation History ({len(history)} messages):\n")
            for msg in history:
                role = "🧑 User" if msg["role"] == "user" else "🤖 Assistant"
                print(f"{role}: {msg['content'][:100]}...")
                print()

    # Handle clear
    if args.clear:
        result = service.clear_conversation()
        print(f"✅ {result['message']}")

    # Handle clear all
    if args.clear_all:
        result = service.clear_all()
        print(f"✅ {result['message']}")

    # If no arguments provided, show help
    if not any([args.upload, args.question, args.info, args.history, args.clear, args.clear_all]):
        parser.print_help()


if __name__ == "__main__":
    main()
