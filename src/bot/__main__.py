"""This file represent startup bot logic."""
import asyncio
import logging

from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio.client import Redis

from src.bot.logic.dreams import periodic_dream_notification, clear_current_records
from src.bot.dispatcher import get_dispatcher, get_redis_storage
from src.bot.structures.data_structure import TransferData
from src.bot.logic.bot_commands import bot_commands
from src.configuration import conf
from src.db.database import create_async_engine


async def start_bot():
    """This function will start bot with polling mode."""
    bot = Bot(token=conf.bot.token)
    job_stores = {
        "default": RedisJobStore(
            jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running",
            host=conf.redis.host, port=conf.redis.port,
            username=conf.redis.username,
            password=conf.redis.passwd
        )
    }
    storage = get_redis_storage(
        redis=Redis(
            db=conf.redis.db,
            host=conf.redis.host,
            password=conf.redis.passwd,
            username=conf.redis.username,
            port=conf.redis.port,
        )
    )

    commands_for_bot = []
    for cmd in bot_commands:
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))

    # scheduler = AsyncIOScheduler(jobstores=job_stores)

    # scheduler.start()
    # scheduler.add_job(periodic_dream_notification, "interval", days=5)
    # scheduler.add_job(clear_current_records, "interval", days=2)

    await bot.set_my_commands(commands=commands_for_bot)

    dp = get_dispatcher(storage=storage)

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        **TransferData(
            engine=create_async_engine(url=conf.db.build_connection_str()),
        )
    )


if __name__ == '__main__':
    logging.basicConfig(level=conf.logging_level)
    asyncio.run(start_bot())
