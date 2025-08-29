"""This file contains build dispatcher logic."""

from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession

from src.configuration import conf

from .logic import routers
from .middlewares.database_md import DatabaseMiddleware
from .middlewares.redis_md import RedisMiddleware



def get_redis_storage(
    redis: Redis, state_ttl=conf.redis.state_ttl, data_ttl=conf.redis.data_ttl
):
    """This function create redis storage or get it forcely from configuration.

    :param redis: Redis client instance
    :param state_ttl: FSM State Time-To-Delete timer in seconds (has effect only
    for Redis database)
    :param data_ttl: FSM Data Time-To-Delete timer in seconds (has effect only
    for Redis database)
    :return: Created Redis storage.
    """
    return RedisStorage(redis=redis, state_ttl=state_ttl, data_ttl=data_ttl)


def get_dispatcher(
    engine: AsyncEngine,
    redis_client: Redis,
    storage: BaseStorage = MemoryStorage(),
    fsm_strategy: FSMStrategy | None = FSMStrategy.CHAT,
    event_isolation: BaseEventIsolation | None = None,
):
    """This function set up dispatcher with routers, filters and middlewares."""
    dp = Dispatcher(
        storage=storage,
        fsm_strategy=fsm_strategy,
        events_isolation=event_isolation,
    )
    for router in routers:
        dp.include_router(router)

    # Create session maker with connection pooling
    sessionmaker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )

    # Register middlewares
    dp.update.middleware.register(DatabaseMiddleware(sessionmaker))
    dp.update.middleware.register(RedisMiddleware(redis_client))

    return dp
