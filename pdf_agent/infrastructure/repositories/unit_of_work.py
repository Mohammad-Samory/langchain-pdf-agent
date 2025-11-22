from typing import Awaitable, Callable, Concatenate, ParamSpec, Self, TypeVar

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from pdf_agent.application.base_service import BaseService
from pdf_agent.infrastructure.database.engine import engine

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T', bound='BaseService')


class UnitOfWork:
    def __init__(self, engine: AsyncEngine):
        self.engine: AsyncEngine = engine
        self.connection: AsyncConnection

    async def __aenter__(self) -> Self:
        self.connection = await self.engine.connect()
        await self.connection.begin()
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object | None) -> None:

        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.connection.close()

    async def commit(self) -> None:
        await self.connection.commit()

    async def rollback(self) -> None:
        await self.connection.rollback()


def with_uow(func: Callable[Concatenate[T, UnitOfWork, P], Awaitable[R]]) -> Callable[Concatenate[T, P], Awaitable[R]]:
    async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        async with UnitOfWork(engine) as uow:
            return await func(self, uow, *args, **kwargs)
    return wrapper  # type: ignore
