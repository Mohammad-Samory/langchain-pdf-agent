from typing import Any, NoReturn

from pydantic import ValidationError


def raise_validation_error(message: str, field: str, input_value: Any = None,
                           error_type: str = 'value_error', title: str | None = None) -> NoReturn:
    raise ValidationError.from_exception_data(title or '', [
        {
            'type': error_type,
            'loc': (field,),
            'input': input_value,
            'ctx': {'error': message}
        }
    ])
