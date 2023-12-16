import logging

import emoji
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.logic.dreams import current_record
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
            f"🌟 *Wanty приглашает вас посмотреть желания!* 🌟\n\n"
            f"👀 Посмотрите, что другие пользователи хотят, и найдите единомышленников.\n ",
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )
    except TelegramForbiddenError as e:
        logging.info(e, exc_info=False)
    except Exception as e:
        logging.error(f"Произошла ошибка при отправке общего уведомления: {e}", exc_info=True)


async def periodic_dream_notification():
    try:
        db = await get_database()
        users = await db.user.get_all_user_id()
        for user in users:
            await send_periodic_notification(user)
    except Exception as e:
        logging.error(e, exc_info=True)


async def clear_current_records():
    current_record.clear()
