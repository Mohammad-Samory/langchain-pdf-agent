from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from pdf_agent.presentation.routes.pdf_routes import router as pdf_router
from pdf_agent.presentation.utils.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title='PDF Q&A Agent',
    description='LangGraph-powered agent for answering questions about PDF documents',
    version='1.0.0',
    lifespan=lifespan
)

register_exception_handlers(app)

# Include routers
app.include_router(pdf_router, prefix='/api', tags=['PDF Q&A'])


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title='PDF Q&A Agent',
        version='1.0.0',
        routes=app.routes
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


@app.get('/health')
async def health_root() -> dict[str, str]:
    return {'message': 'PDF Q&A Agent is running'}


@app.get('/')
async def read_root() -> dict[str, str]:
    return {'message': 'Welcome to PDF Q&A Agent - use /api/upload to upload PDFs and /api/ask to ask questions'}
