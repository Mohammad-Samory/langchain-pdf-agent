import inspect

from fastapi import APIRouter

from pdf_agent.errors import AppError, Errors
from pdf_agent.presentation.models.shared import MainResponse
from pdf_agent.presentation.utils.response import get_ok

errors_router = APIRouter(prefix='/errors', tags=['Errors'])


@errors_router.get('')
async def get_all() -> MainResponse[list[dict[str, str]]]:
    errors = [
        {'code': value.code, 'message': value.message, 'description': value.description}
        for _, value in inspect.getmembers(Errors)
        if isinstance(value, AppError)
    ]
    return get_ok(errors)
