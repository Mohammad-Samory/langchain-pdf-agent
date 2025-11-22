from enum import Enum
from typing import Any, Tuple, Type

from sqlalchemy.engine import Dialect
from sqlalchemy.types import String, TypeDecorator


class StrEnum(TypeDecorator[Enum]):
    """SQLAlchemy TypeDecorator so that we can store enums as strings in the database.
    By default, SQLAalchemy will store `.name` in the database, but we override this logic to
    allow us to reduce the use of casting to `EnumType(value)`, and reduce the use of the
    `.value` property when using the field elsewhere.
    """
    impl = String
    cache_ok = True

    def __init__(self, enumtype: Type[Enum], *args: Tuple[Any], **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value: Enum | str | None, dialect: Dialect) -> str | None:
        if value:
            return value.value if isinstance(value, Enum) else value
        return None

    def process_result_value(self, value: str | None, dialect: Dialect) -> Enum | None:
        return self._enumtype(value) if value is not None else None


# class HolidayType(StrEnum, str, Enum):
#     RELIGIOUS = 'religious'
#     NATIONAL = 'national'
