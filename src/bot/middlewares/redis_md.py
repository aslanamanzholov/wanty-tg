"""Redis middleware for cache initialization."""
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from src.bot.structures.data_structure import TransferData
from src.bot.structures.redis_cache import RedisCache


class RedisMiddleware(BaseMiddleware):
    """This middleware initializes Redis cache for handlers."""

    def __init__(self, redis_client: Redis):
        """Initialize Redis middleware."""
        super().__init__()
        self.redis_client = redis_client

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: TransferData,
    ) -> Any:
        """Initialize Redis cache for each update."""
        # Инициализируем Redis кэш
        redis_cache = RedisCache(self.redis_client)
        data['redis_cache'] = redis_cache
        
        # Инициализируем глобальную переменную для dreams/select.py
        from src.bot.logic.dreams.select import redis_cache as global_redis_cache
        global_redis_cache = redis_cache
        
        return await handler(event, data)
