# 📁 Project Structure

```
agent/
│
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # 5-minute setup guide
├── 📄 WINDOWS_SETUP.md             # Windows-specific instructions
├── 📄 PROJECT_SUMMARY.md           # Transformation summary
├── 📄 TESTING.md                   # Testing guide
│
├── 🐍 ask.py                       # CLI tool for Q&A
├── 🔧 setup.sh                     # Linux/Mac setup script
├── 🔧 setup.ps1                    # Windows setup script
│
├── 📦 requirements.txt             # Python dependencies (frozen)
├── 📦 requirements.top             # Top-level dependencies
├── ⚙️ setup.cfg                    # Tool configurations (flake8, mypy, pytest)
│
├── 🐳 Dockerfile                   # Container definition
├── 🐳 compose.yml                  # Docker Compose configuration
├── 📝 alembic.ini                  # Database migration config (optional)
│
├── 🔨 Makefile                     # Build automation (Linux/Mac)
├── 🔨 Makefile.windows             # Build automation (Windows)
├── 🔨 gunicorn_conf.py             # Production server config
│
├── 🔒 .env.example                 # Environment template
├── 🚫 .gitignore                   # Git ignore rules
├── 🚫 .dockerignore                # Docker ignore rules
│
├── 📂 .github/                     # GitHub workflows
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── dev.yml
│       ├── main.yml
│       ├── production.yml
│       └── staging.yml
│
├── 📂 bin/                         # Scripts
│   ├── boot.sh                     # Linux startup script
│   ├── boot.ps1                    # Windows startup script
│   ├── boot.bat                    # Windows batch wrapper
│   ├── refreeze.sh                 # Linux dependency management
│   ├── refreeze.ps1                # Windows dependency management
│   ├── refreeze.bat                # Windows batch wrapper
│   └── wait-for-it.sh              # Database wait script
│
└── 📂 pdf_agent/                   # Main application package
    │
    ├── 📄 __init__.py              # Package initialization
    ├── 🚀 app.py                   # FastAPI application entry point
    │
    ├── 📂 domain/                  # 🏛️ DOMAIN LAYER - Business Logic
    │   ├── shared/
    │   │   ├── base_entity.py      # Base entity class
    │   │   └── enumerations.py     # Shared enums
    │   └── pdf/
    │       ├── __init__.py
    │       ├── pdf_document.py     # PDF Document aggregate
    │       └── conversation.py     # Conversation entity
    │
    ├── 📂 application/             # 🎯 APPLICATION LAYER - Use Cases
    │   ├── base_service.py         # Base service class
    │   ├── agent/
    │   │   ├── __init__.py
    │   │   └── pdf_qa_agent.py     # LangGraph React agent ⭐
    │   └── services/
    │       ├── __init__.py
    │       └── pdf_qa_service.py   # PDF Q&A orchestration service
    │
    ├── 📂 infrastructure/          # 🔌 INFRASTRUCTURE LAYER - External Services
    │   ├── pdf/
    │   │   ├── __init__.py
    │   │   └── pdf_processor.py    # PDF extraction & chunking
    │   ├── vectorstore/
    │   │   ├── __init__.py
    │   │   └── vector_store.py     # FAISS vector store wrapper
    │   ├── database/               # Database (optional)
    │   │   ├── engine.py
    │   │   ├── schema.py
    │   │   └── alembic/
    │   └── repositories/           # Repositories (optional)
    │       ├── base_repository.py
    │       └── unit_of_work.py
    │
    ├── 📂 presentation/            # 🌐 PRESENTATION LAYER - API
    │   ├── routes/
    │   │   ├── errors.py
    │   │   └── pdf_routes.py       # PDF Q&A endpoints ⭐
    │   ├── models/
    │   │   └── shared.py
    │   └── utils/
    │       ├── exception_handlers.py
    │       ├── response.py
    │       └── validation.py
    │
    ├── 📂 configs/                 # ⚙️ Configuration
    │   ├── env.py                  # Environment variables
    │   └── log.py                  # Logging configuration
    │
    ├── 📂 errors/                  # ❌ Error Handling
    │   ├── __init__.py
    │   ├── app_errors.py
    │   └── app_exceptions.py
    │
    ├── 📂 utils/                   # 🛠️ Utilities
    │   └── date_parser.py
    │
    └── 📂 tests/                   # 🧪 Tests
        ├── __init__.py
        ├── conftest.py             # Test fixtures
        └── test_pdf_qa_service.py  # Service tests
```

## 🎯 Key Components

### Core Features

- **🤖 LangGraph Agent** (`application/agent/pdf_qa_agent.py`)

  - React-style reasoning loop
  - Vector search tool integration
  - Conversational with history

- **🔍 Vector Store** (`infrastructure/vectorstore/vector_store.py`)

  - FAISS-based similarity search
  - HuggingFace embeddings
  - In-memory for speed

- **📄 PDF Processor** (`infrastructure/pdf/pdf_processor.py`)

  - Text extraction with pdfplumber
  - Semantic chunking with LangChain
  - Page number preservation

- **🌐 API Routes** (`presentation/routes/pdf_routes.py`)
  - Upload endpoint
  - Ask endpoint
  - Document management

### Entry Points

1. **Web API**: `pdf_agent/app.py` → FastAPI server
2. **CLI**: `ask.py` → Command-line interface
3. **Docker**: `compose.yml` → Containerized deployment

## 📊 Architecture Flow

```
User Request
    ↓
[Presentation Layer]
    pdf_routes.py → Validates request
    ↓
[Application Layer]
    pdf_qa_service.py → Orchestrates
    ↓
    pdf_qa_agent.py → LangGraph agent
    ↓
[Infrastructure Layer]
    vector_store.py → Searches vectors
    ↓
[Domain Layer]
    conversation.py → Manages state
    ↓
Response to User
```

## 🚀 Quick Access

### Main Files to Know

1. `README.md` - Start here for full documentation
2. `QUICKSTART.md` - Get running in 5 minutes
3. `ask.py` - CLI for quick testing
4. `.env.example` - Configuration template

### Development Files

1. `pdf_agent/app.py` - Application entry
2. `pdf_agent/application/agent/pdf_qa_agent.py` - Agent logic
3. `pdf_agent/presentation/routes/pdf_routes.py` - API endpoints
4. `pdf_agent/application/services/pdf_qa_service.py` - Service layer

### Configuration Files

1. `.env` - Your environment (create from .env.example)
2. `setup.cfg` - Linting and testing config
3. `compose.yml` - Docker services
4. `requirements.txt` - Python packages

## 📈 Project Statistics

- **Total Files**: ~40+ files
- **Lines of Code**: ~2500+ lines
- **Layers**: 4 (Domain, Application, Infrastructure, Presentation)
- **Patterns**: DDD, Clean Architecture, SOLID
- **Technologies**: 10+ (LangChain, LangGraph, FastAPI, etc.)

## 🎓 Learning Resources

- Domain entities: `pdf_agent/domain/`
- LangGraph agent: `pdf_agent/application/agent/`
- API design: `pdf_agent/presentation/routes/`
- Infrastructure: `pdf_agent/infrastructure/`

---

**Navigate with confidence! Each layer has a clear responsibility.** 🗺️
