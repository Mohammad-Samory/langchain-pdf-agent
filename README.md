# PDF Q&A Agent with LangGraph

A LangGraph React-style conversational agent that answers questions about PDF documents using vector search and LLM reasoning. Built with FastAPI and domain-driven design principles.

## 🚀 Features

- **PDF Ingestion**: Upload and automatically process PDF documents
- **Intelligent Chunking**: Text is split into semantic chunks with page number tracking
- **Vector Search**: FAISS-based similarity search with HuggingFace embeddings
- **LangGraph Agent**: React-style agent that decides when to search the document
- **Conversational**: Maintains context across multiple questions
- **Source Citations**: Answers include page number references
- **FastAPI REST API**: Clean, modern API with automatic documentation
- **Domain-Driven Design**: Clean architecture with separated layers

## 📋 Prerequisites

- Docker Desktop (with WSL 2 backend for Windows)
- Python 3.13+ (for local development)
- OpenAI API Key

## 🛠️ Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional (with defaults)
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Get your OpenAI API key from https://platform.openai.com/api-keys

### 2. Run with Docker (Recommended)

```bash
# Build and start
docker-compose build pdf-agent
docker-compose up pdf-agent
```

The API will be available at: **http://localhost:8200**

### 3. Local Development (Without Docker)

**Windows:**

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn pdf_agent.app:app --reload --host 0.0.0.0 --port 8200
```

**Linux/Mac:**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn pdf_agent.app:app --reload --host 0.0.0.0 --port 8200
```

## 📚 Usage

### API Endpoints

#### 1. Health Check

```bash
GET http://localhost:8200/health
```

#### 2. Upload PDF

```bash
POST http://localhost:8200/api/upload
Content-Type: multipart/form-data

file: <your-pdf-file>
```

**Example with curl:**

```bash
curl -X POST "http://localhost:8200/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf"
```

**Example with PowerShell:**

```powershell
$file = Get-Item "C:\path\to\document.pdf"
Invoke-RestMethod -Uri "http://localhost:8200/api/upload" -Method Post -Form @{file=$file}
```

**Response:**

```json
{
  "status": "success",
  "filename": "document.pdf",
  "total_pages": 25,
  "total_chunks": 150,
  "message": "PDF 'document.pdf' successfully uploaded and indexed"
}
```

#### 3. Ask Questions

```bash
POST http://localhost:8200/api/ask
Content-Type: application/json

{
  "question": "What are the main findings of this document?"
}
```

**Example with curl:**

```bash
curl -X POST "http://localhost:8200/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main findings?"}'
```

**Example with PowerShell:**

```powershell
$body = @{ question = "What are the main findings?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8200/api/ask" -Method Post -Body $body -ContentType "application/json"
```

**Response:**

```json
{
  "answer": "According to the document, the main findings are...",
  "sources": [
    { "page": 3, "type": "reference" },
    { "page": 7, "type": "reference" }
  ]
}
```

#### 4. Get Document Info

```bash
GET http://localhost:8200/api/document
```

#### 5. Get Conversation History

```bash
GET http://localhost:8200/api/conversation
```

#### 6. Clear Conversation

```bash
DELETE http://localhost:8200/api/conversation
```

#### 7. Clear Everything

```bash
DELETE http://localhost:8200/api/all
```

### Interactive API Documentation

Visit **http://localhost:8200/docs** for Swagger UI with interactive API testing.

## 🏗️ Architecture & Design

### Domain-Driven Design Structure

```
pdf_agent/
├── domain/                    # Business entities and logic
│   ├── pdf/
│   │   ├── pdf_document.py   # PDF document aggregate
│   │   └── conversation.py   # Conversation entity
│   └── shared/
│       └── base_entity.py    # Base entity class
├── application/               # Application services and use cases
│   ├── agent/
│   │   └── pdf_qa_agent.py  # LangGraph agent implementation
│   └── services/
│       └── pdf_qa_service.py # PDF Q&A service
├── infrastructure/            # External services and data access
│   ├── pdf/
│   │   └── pdf_processor.py # PDF text extraction and chunking
│   └── vectorstore/
│       └── vector_store.py  # FAISS vector store wrapper
├── presentation/              # API layer
│   ├── routes/
│   │   └── pdf_routes.py    # FastAPI routes
│   └── utils/
│       └── exception_handlers.py
└── configs/                   # Configuration
    ├── env.py                # Environment variables
    └── log.py                # Logging configuration
```

### Design Decisions

#### 1. **LangGraph React Agent**

- Uses the React pattern (Reason-Act-Observe)
- Agent decides when to invoke vector search tool
- Maintains conversation state across turns
- Tools are bound to the LLM for autonomous decision-making

#### 2. **Vector Store (FAISS)**

- In-memory for fast performance
- Uses sentence-transformers for embeddings (no API calls needed)
- Similarity search with configurable `k` and threshold
- Metadata includes page numbers for citation

#### 3. **PDF Processing**

- `pdfplumber` for accurate text extraction
- `RecursiveCharacterTextSplitter` for semantic chunking
- Preserves page numbers throughout the pipeline
- Configurable chunk size and overlap

#### 4. **Conversation Management**

- Domain entity tracks message history
- Context passed to agent for follow-up questions
- Source citations stored with assistant messages

#### 5. **Clean Architecture**

- **Domain Layer**: Pure business logic, no dependencies
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: External integrations (PDF, vector DB, LLM)
- **Presentation Layer**: HTTP API endpoints

## 🔧 Development

### Update Dependencies

```bash
# Windows
.\bin\refreeze.ps1

# Linux/Mac
./bin/refreeze.sh
```

## 📖 Key Technologies

- **LangChain**: Framework for LLM applications
- **LangGraph**: State machine for agent workflows
- **OpenAI**: GPT models for reasoning
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Local embeddings
- **pdfplumber**: PDF text extraction
- **FastAPI**: Modern web framework
- **Pydantic**: Data validation
- **Docker**: Containerization

## 🔍 How It Works

1. **PDF Upload**:

   - User uploads PDF via `/api/upload`
   - `PDFProcessor` extracts text with page numbers
   - Text is chunked using recursive splitting
   - Chunks are embedded and stored in FAISS

2. **Question Asked**:

   - User sends question to `/api/ask`
   - Question added to conversation history
   - Agent receives question + conversation context

3. **Agent Reasoning**:

   - LLM decides if it needs to search the PDF
   - If yes: calls `search_pdf` tool
   - Tool performs vector similarity search
   - Returns relevant chunks with page numbers
   - LLM synthesizes final answer from chunks
   - Answer includes page citations

4. **Response**:
   - Answer returned to user
   - Conversation history updated
   - Sources (page numbers) included

## 🚨 Common Issues

| Issue                      | Solution                                                    |
| -------------------------- | ----------------------------------------------------------- |
| "No PDF has been uploaded" | Upload a PDF first using `/api/upload`                      |
| "OpenAI API key not found" | Set `OPENAI_API_KEY` in `.env` file                         |
| Docker not starting        | Ensure Docker Desktop is running                            |
| Port already in use        | Change port in `compose.yml` or stop other services on 8200 |

## 📝 Example Session

```bash
# 1. Upload PDF
curl -X POST http://localhost:8200/api/upload \
  -F "file=@research_paper.pdf"

# Response: {"status": "success", "total_pages": 15, "total_chunks": 89}

# 2. Ask first question
curl -X POST http://localhost:8200/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main hypothesis?"}'

# Response: {"answer": "The main hypothesis, as stated on Page 3, is...", "sources": [{"page": 3}]}

# 3. Ask follow-up
curl -X POST http://localhost:8200/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What evidence supports this?"}'

# Response: {"answer": "The evidence includes... (Page 5, 7)", "sources": [{"page": 5}, {"page": 7}]}
```

## 📚 References

- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangChain Vector Stores](https://docs.langchain.com/oss/python/integrations/vectorstores)
- [RecursiveTextSplitter](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)
- [LangChain YouTube Channel](https://www.youtube.com/@LangChain)

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please follow the domain-driven design structure and include tests.

---

**Built with ❤️ using LangGraph and FastAPI**
