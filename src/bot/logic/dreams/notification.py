import emoji
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.logic.dreams import current_record
from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.configuration import conf
from src.db.database import create_async_engine, Database


async def periodic_dream_notification():
    bot = Bot(token=conf.bot.token)
    async with AsyncSession(bind=create_async_engine(url=conf.db.build_connection_str())) as session:
        db = Database(session)
    users = await db.user.get_all_user_id()
    for user in users:
        await bot.send_message(user.user_id, f"Привет *{user.name if user else 'пользователь'}!*\n"
                                             f"Только активные пользователи узнают все тайны Wanty. Будь среди первых! "
                                             f"{emoji.emojize(':thought_balloon:')}",
                               reply_markup=MENU_KEYBOARD, parse_mode="MARKDOWN")


async def clear_current_records():
    current_record.clear()
