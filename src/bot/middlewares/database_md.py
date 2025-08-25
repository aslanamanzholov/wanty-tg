"""Database middleware is a common way to inject database dependency in handlers."""
from collections.abc import Awaitable, Callable
from typing import Any
import asyncio

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.bot.structures.data_structure import TransferData
from src.db.database import Database


class DatabaseMiddleware(BaseMiddleware):
    """This middleware throw a Database class to handler with connection pooling."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        """Initialize middleware with session maker."""
        super().__init__()
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: TransferData,
    ) -> Any:
        """This method calls every update with optimized session management."""
        async with self.sessionmaker() as session:
            data['db'] = Database(session)
            try:
                return await handler(event, data)
            except Exception as e:
                await session.rollback()
                raise e
