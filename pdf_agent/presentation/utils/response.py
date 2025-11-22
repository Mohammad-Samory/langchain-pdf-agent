import json
from datetime import date, datetime, time
from typing import Any, List, Optional, Type, TypeVar, Union, cast
from uuid import UUID

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pdf_agent.utils.date_parser import date_to_iso_str, datetime_to_iso_str, time_to_str


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return datetime_to_iso_str(obj)
        if isinstance(obj, date):
            return date_to_iso_str(obj)
        if isinstance(obj, time):
            return time_to_str(obj)

        return super().default(obj)


class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(content, cls=CustomJSONEncoder).encode('utf-8')


T = TypeVar('T')  # Data type
B = TypeVar('B', bound=BaseModel)  # Data type

DataType = Optional[Union[B, List[B], dict[str, Any], list[dict[str, Any]]]]


def get_response(status_code: int,
                 message: str,
                 data: DataType[B] = None,
                 errors: Optional[dict[str, Any] | list[dict[str, Any]] | str] = None,
                 extra: Optional[dict[str, Any]] = None,
                 ) -> CustomJSONResponse:
    serialized_data: Optional[Union[dict[str, Any], list[dict[str, Any]]]] = None

    if data is not None:
        if isinstance(data, list):
            serialized_data = [item.model_dump() if isinstance(item, BaseModel) else item for item in data]
        elif isinstance(data, BaseModel):
            serialized_data = data.model_dump()
        elif isinstance(data, dict):
            serialized_data = data
    content: dict[str, Any] = {'status_code': status_code, 'message': message}
    if serialized_data is not None:
        content['data'] = serialized_data
    if errors:
        content['errors'] = errors
    content.update(extra or {})
    return CustomJSONResponse(status_code=status_code, content=content)


def get_ok(data: DataType[B], extra: Optional[dict[str, Any]] = {}, message: str = 'Ok',
           return_type: Optional[Type[T]] = None) -> T:
    return cast(T, get_response(status.HTTP_200_OK, message, data, None, extra))


def get_bad_request(message: str = 'Bad Request',
                    errors: Optional[dict[str, Any] | list[dict[str, Any]] | str] = None,
                    return_type: Optional[Type[T]] = None) -> T:
    return cast(T, get_response(status.HTTP_400_BAD_REQUEST, message, None, errors))


def get_unauthorized(message: str = 'Unauthorized',
                     errors: Optional[dict[str, Any] | list[dict[str, Any]] | str] = None,
                     return_type: Optional[Type[T]] = None) -> T:
    return cast(T, get_response(status.HTTP_401_UNAUTHORIZED, message, None, errors))


def get_forbidden(message: str = 'Forbidden',
                  errors: Optional[dict[str, Any] | list[dict[str, Any]] | str] = None,
                  return_type: Optional[Type[T]] = None) -> T:
    return cast(T, get_response(status.HTTP_403_FORBIDDEN, message, None, errors))


def get_not_found(message: str = 'Not Found',
                  errors: Optional[dict[str, Any] | list[dict[str, Any]] | str] = None,
                  return_type: Optional[Type[T]] = None) -> T:
    return cast(T, get_response(status.HTTP_404_NOT_FOUND, message, errors=errors))


def get_method_not_allowed(message: str = 'Method Not Allowed',
                           errors: Optional[dict[str, Any] | list[dict[str, Any]] | str] = None,
                           return_type: Optional[Type[T]] = None) -> T:
    return cast(T, get_response(status.HTTP_405_METHOD_NOT_ALLOWED, message, None, errors))


def get_server_error(message: str = 'Internal Server Error',
                     errors: Optional[dict[str, Any] | list[dict[str, Any]] | str] = None,
                     return_type: Optional[Type[T]] = None) -> T:
    return cast(T, get_response(status.HTTP_500_INTERNAL_SERVER_ERROR, message, None, errors))
