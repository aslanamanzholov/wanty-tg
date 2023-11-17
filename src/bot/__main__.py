"""This file represent startup bot logic."""
import asyncio
import logging

from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio.client import Redis

from src.bot.logic.dreams import periodic_dream_notification
from src.bot.dispatcher import get_dispatcher, get_redis_storage
from src.bot.structures.data_structure import TransferData
from src.bot.logic.bot_commands import bot_commands
from src.configuration import conf
from src.db.database import create_async_engine

scheduler = AsyncIOScheduler()


async def start_bot():
    """This function will start bot with polling mode."""
    bot = Bot(token=conf.bot.token)
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

    scheduler.start()
    scheduler.add_job(periodic_dream_notification, "interval", days=3)

    await bot.set_my_commands(commands=commands_for_bot)

    dp = get_dispatcher(storage=MemoryStorage())

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
