from abc import ABC
from typing import Any, Callable, Generic, List, Type, TypeVar
from uuid import UUID

from sqlalchemy import Row, Table, and_, asc, case, delete, desc, func, insert, literal_column, select, update
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import operators
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import Function
from sqlalchemy.sql.selectable import Select
from sqlalchemy.types import Boolean, Date, DateTime, Float, Integer, String

from pdf_agent.domain.shared.base_entity import BaseEntityBase
from pdf_agent.errors import DatabaseException
from pdf_agent.utils.date_parser import iso_str_to_datetime, str_to_date

supported_operators = ['=', '!=', '>', '>=', '<', '<=', 'like', 'ilike', 'in', 'not_in']

# Supported operators mapping
OPERATORS_MAPPING: dict[str, Callable[..., Any]] = {
    '=': operators.eq,
    '!=': operators.ne,
    '>': operators.gt,
    '>=': operators.ge,
    '<': operators.lt,
    '<=': operators.le,
    'like': operators.like_op,
    'ilike': operators.ilike_op,
    'in': lambda col, val: col.in_(val),
    'not_in': lambda col, val: ~col.in_(val),
}


T = TypeVar('T', bound=BaseEntityBase)


class BaseRepository(ABC, Generic[T]):
    def __init__(self, connection: AsyncConnection, model_cls: Type[T], table: Table):
        self.connection = connection
        self.table = table
        self.model_cls = model_cls

    async def add(self, entity: T, include_id: bool = False) -> T:
        excluded_fields = list(entity.config.db_excluded_fields)
        if not include_id:
            excluded_fields.append('id')
            excluded_fields.append('created_at')
        data = entity.to_dict(excluded_fields, False)
        cmd = insert(self.table).values(**data).returning(*self.table.columns)
        result = await self.connection.execute(cmd)
        row = result.first()
        if not row:
            raise DatabaseException('Filed to create row', self.model_cls.__name__, self.table.name)
        return self._map_row_to_model(row)

    async def get_by_id(self, id: UUID) -> T | None:
        cmd = self._get_select_statement().where(self.table.c.id == id)
        result = await self.connection.execute(cmd)
        row = result.first()
        return self._map_row_to_model(row) if row else None

    async def get_all(self, filters: dict[str, Any] | None = None,
                      sort_by: str = 'created_at', order: str = 'desc') -> List[T]:
        cmd = self._get_select_with_filters(filters, sort_by, order)
        result = await self.connection.execute(cmd)
        return [self._map_row_to_model(row) for row in result.all()]

    async def get_paginated(self, page: int, limit: int,
                            sort_by: str = 'created_at', order: str = 'desc') -> tuple[List[T], int]:
        return await self.get_paginated_with_filters(page, limit, None, sort_by, order)

    async def get_paginated_with_filters(self, page: int, limit: int, filters: dict[str, Any] | None = None,
                                         sort_by: str = 'created_at', order: str = 'desc') -> tuple[List[T], int]:

        cmd = self._get_select_with_filters(filters, sort_by, order)

        # Query to get the total count
        count_cmd = cmd.with_only_columns(func.count(self.table.c.id).label('total')).order_by(None)

        total_result = await self.connection.execute(count_cmd)
        total = total_result.scalar_one()

        # Query to get paginated data
        paginated_cmd = cmd.offset((page - 1) * limit).limit(limit)
        rows = await self.connection.execute(paginated_cmd)

        return [self._map_row_to_model(row) for row in rows.all()], total

    async def update(self, id: UUID, data: dict[str, Any]) -> T:
        invalid_keys = [k for k in data if k not in self.table.c
                        and k not in self.model_cls.config.db_excluded_fields]
        if invalid_keys:
            raise DatabaseException(
                f"Invalid column(s) in data: {', '.join(invalid_keys)}",
                self.model_cls.__name__,
                self.table.name)

        update_data = {k: v for k, v in data.items() if k not in self.model_cls.config.db_excluded_fields}
        cmd = update(self.table).where(self.table.c.id == id).values(**update_data).returning(*self.table.columns)
        result = await self.connection.execute(cmd)
        row = result.first()
        if not row:
            raise DatabaseException('Field to update row', self.model_cls.__name__, self.table.name)
        return self._map_row_to_model(row)

    async def delete(self, id: UUID) -> T:
        cmd = delete(self.table).where(self.table.c.id == id).returning(*self.table.columns)
        result = await self.connection.execute(cmd)
        row = result.first()
        if not row:
            raise DatabaseException('Field to delete row', self.model_cls.__name__, self.table.name)
        return self._map_row_to_model(row)

    async def bulk_insert(self, entities: list[T]) -> list[T]:
        if not entities:
            raise DatabaseException('there is no data to insert', self.model_cls.__name__, self.table.name)

        data = [
            {
                **entity.to_dict(entity.config.db_excluded_fields + ['id', 'created_at'], False)
            }
            for entity in entities
        ]
        stmt = self.table.insert().returning(*self.table.columns)
        result = await self.connection.execute(stmt, data)
        return [self._map_row_to_model(row) for row in result.all()]

    async def bulk_update(self, updates: list[dict[str, Any]]) -> list[T]:
        if not updates:
            raise DatabaseException('there is no data to update', self.model_cls.__name__, self.table.name)
        for data in updates:
            invalid_keys = [k for k in data if k not in self.table.c
                            and k not in self.model_cls.config.db_excluded_fields]
            if invalid_keys:
                raise DatabaseException(
                    f"Invalid column(s) in update data: {', '.join(invalid_keys)}",
                    self.model_cls.__name__,
                    self.table.name)

        keys = [key for key in updates[0].keys() if key != 'id']
        case_statements = {
            col: case(
                *[
                    (self.table.c.id == update['id'], update[col])
                    for update in updates if col in update
                ],
                else_=getattr(self.table.c, col)
            )
            for col in keys
        }

        stmt = (
            update(self.table)
            .where(self.table.c.id.in_([update['id'] for update in updates]))
            .values(case_statements)
            .returning(*self.table.columns)
        )
        result = await self.connection.execute(stmt)
        return [self._map_row_to_model(row) for row in result.all()]

    async def bulk_delete(self, ids: list[UUID]) -> list[T]:
        if not ids:
            raise DatabaseException('there is no data to delete', self.model_cls.__name__, self.table.name)

        stmt = delete(self.table).where(self.table.c.id.in_(ids)).returning(*self.table.columns)
        result = await self.connection.execute(stmt)
        return [self._map_row_to_model(row) for row in result.all()]

    def _get_select_statement(self) -> Select[tuple[Any]]:
        return select(self.table)

    def _get_select_with_filters(self, filters: dict[str, Any] | None = None,
                                 sort_by: str = 'created_at', order: str = 'desc') -> Select[tuple[Any]]:
        cmd = self._get_select_statement()

        expressions = self._parse_filters(filters)
        if expressions is not None:
            cmd = cmd.where(expressions)

        if sort_by not in self.table.c:
            return cmd

        return cmd.order_by(asc(self.table.c[sort_by])if order == 'asc' else desc(self.table.c[sort_by]))

    def _parse_filters(self, filters: dict[str, Any] | None = None) -> ColumnElement[bool] | None:
        if not filters:
            return None
        expressions: List[Any] = []

        for key, value in filters.items():
            column_name, operator = key.split(':') if ':' in key else (key, '=')

            if operator not in OPERATORS_MAPPING or column_name not in self.table.c:
                continue
            column = self.table.c[column_name]
            is_list_op = operator in ['in', 'not_in']

            try:
                if isinstance(column.type, Integer):
                    if is_list_op:
                        value = [int(v) for v in value.split(',')] if isinstance(value, str) else value
                    else:
                        value = int(value)
                elif isinstance(column.type, Float):
                    if is_list_op:
                        value = [float(v) for v in value.split(',')] if isinstance(value, str) else value
                    else:
                        value = float(value)
                elif isinstance(column.type, Boolean):
                    value = value.lower() in ['true', '1'] if isinstance(value, str)else bool(value)
                elif isinstance(column.type, DateTime):
                    value = iso_str_to_datetime(value)
                    if not value:
                        continue
                elif isinstance(column.type, Date):
                    value = str_to_date(value)
                    if not value:
                        continue
                elif isinstance(column.type, String):
                    if is_list_op:
                        value = value.split(',') if isinstance(value, str) else value
                expressions.append(OPERATORS_MAPPING[operator](column, value))
            except Exception:
                continue

        return and_(*expressions) if expressions else None

    def _map_row_to_model(self, row: Row[Any]) -> T:
        return self.model_cls.from_dict(dict(row._mapping))

    def _build_json_object(self, table: Table) -> Function[Any]:
        return func.json_build_object(*sum([[literal_column(f"'{col}'"), table.c[col]] for col in table.c.keys()], []))
