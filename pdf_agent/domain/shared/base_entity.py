from dataclasses import dataclass, fields
from datetime import date, datetime
from enum import Enum
from types import UnionType
from typing import Any, Type, TypeVar, get_args, get_origin
from uuid import UUID

from pdf_agent.utils.date_parser import date_to_iso_str, datetime_to_iso_str

T = TypeVar('T', bound='BaseEntityBase')


def get_field_value(field_type: type[Any] | str | Any, filed_data: Any) -> Any:
    if filed_data is None:
        return None
    if isinstance(field_type, type) and issubclass(field_type, BaseEntityBase):
        return field_type.from_dict(filed_data)

    origin = get_origin(field_type)
    if (origin is list or origin is UnionType) and isinstance(filed_data, list):
        args = get_args(field_type) or ()
        if origin is UnionType:
            args = get_args(args[0]) or ()
        if args and isinstance(args[0], type) and issubclass(args[0], BaseEntityBase):
            return [args[0].from_dict(item) for item in filed_data]

    return filed_data


def get_attr_value(attr_val: Any, map_primitive: bool = True) -> Any:
    if attr_val is None:
        return None

    if isinstance(attr_val, BaseEntityBase):
        return attr_val.to_dict()

    if isinstance(attr_val, list):
        return [get_attr_value(item) for item in attr_val]

    if not map_primitive:
        return attr_val

    if isinstance(attr_val, UUID):
        return str(attr_val)

    if isinstance(attr_val, datetime):
        return datetime_to_iso_str(attr_val)

    if isinstance(attr_val, date):
        return date_to_iso_str(attr_val)

    if isinstance(attr_val, Enum):
        return attr_val.value

    return attr_val


@dataclass
class BaseEntityBase:
    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any], exclude: list[str] | None = None) -> T:
        """
        Convert a dictionary to an instance of the class.
        Recursively handles nested data classes and lists of data classes.
        """
        excluded_fields = list(cls.config.from_dict_excluded_fields)
        if exclude:
            excluded_fields = excluded_fields + exclude

        instance_data = {}
        entity_fields = {f.name: f.type for f in fields(cls)}
        for field_name, field_type in entity_fields.items():
            field_data = None
            if field_name not in excluded_fields:
                field_data = data.get(field_name, None)
            instance_data[field_name] = get_field_value(field_type, field_data)

        return cls(**instance_data)

    def to_dict(self, exclude: list[str] | None = None, map_primitive: bool = True) -> dict[str, Any]:
        """
        Convert the current object to a dictionary and handle nested dataclasses.
        Recursively converts all nested dataclasses to dictionaries.
        """
        excluded_fields = list(self.config.to_dict_excluded_fields)
        if exclude:
            excluded_fields = excluded_fields + exclude

        data: dict[str, Any] = {}
        for cls in self.__class__.mro():
            if not hasattr(cls, '__annotations__'):
                continue
            entity_fields = [f.name for f in fields(cls)]
            for field_name in entity_fields:
                if field_name not in excluded_fields:
                    data[field_name] = get_attr_value(getattr(self, field_name, None), map_primitive)

        return data

    def update_from_dict(self, data: dict[str, Any]) -> None:

        entity_fields = {f.name: f.type for f in fields(self)}
        for field_name, field_type in entity_fields.items():
            if field_name not in data:
                continue

            value = data[field_name]
            if not value:
                setattr(self, field_name, value)
                continue
            self._set_field_value(field_name, field_type, value)

    def _set_field_value(self, field_name: str, field_type: type[Any] | str | Any, data: Any) -> None:
        if isinstance(field_type, type) and issubclass(field_type, BaseEntityBase):
            obj = getattr(self, field_name, None)
            if obj:
                obj.update_from_dict(data)
            else:
                setattr(self, field_name, field_type.from_dict(data))
            return
        origin = getattr(field_type, "__origin__", None)
        if origin is list and isinstance(data, list):
            args = getattr(field_type, "__args__", [])
            if args and isinstance(args[0], type) and issubclass(args[0], BaseEntityBase):
                setattr(self, field_name, [args[0].from_dict(item) for item in data])

        setattr(self, field_name, data)

    class config:
        db_excluded_fields: list[str] = []
        to_dict_excluded_fields: list[str] = []
        from_dict_excluded_fields: list[str] = []


@dataclass
class BaseEntity(BaseEntityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
