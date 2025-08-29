import logging
import asyncio
from typing import List

import emoji
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.configuration import conf
from src.db.database import create_async_engine, Database


async def get_bot():
    return Bot(token=conf.bot.token)


async def get_database():
    async with AsyncSession(bind=create_async_engine(url=conf.db.build_connection_str())) as session:
        return Database(session)


async def send_periodic_notification(user):
    bot = await get_bot()
    try:
        await bot.send_message(
            user.user_id,
            f"🌟 *Wanty приглавает вас посмотреть желания!* 🌟\n\n"
            f"👀 Посмотрите, что другие пользователи хотят, и найдите единомышленников.\n ",
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )
    except TelegramForbiddenError as e:
        logging.info(e, exc_info=False)
    except Exception as e:
        logging.error(f"Произошла ошибка при отправке общего уведомления: {e}", exc_info=True)


async def send_batch_notifications(users: List, batch_size: int = 10):
    """Отправляет уведомления батчами для оптимизации."""
    bot = await get_bot()
    
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        tasks = []
        
        for user in batch:
            task = send_periodic_notification(user)
            tasks.append(task)
        
        # Выполняем батч асинхронно
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Небольшая пауза между батчами для избежания rate limiting
        await asyncio.sleep(0.1)


async def periodic_dream_notification():
    try:
        db = await get_database()
        users = await db.user.get_all_user_id()
        
        # Используем batch отправку для оптимизации
        await send_batch_notifications(users, batch_size=20)
        
    except Exception as e:
        logging.error(e, exc_info=True)


async def clear_current_records():
    """Очистка записей теперь не нужна - используется Redis кэш."""
    logging.info("Очистка записей не требуется - используется Redis кэш")
