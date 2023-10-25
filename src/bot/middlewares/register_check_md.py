"""Role middleware used for get role of user for followed filtering."""
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.bot.structures.data_structure import UserCheckRegisterTransferData
from src.bot.structures.fsm.menu import MENU_KEYBOARD
from src.db import Database


class RegisterCheckMiddleware(BaseMiddleware):
    """This class is used for getting user role from database."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: UserCheckRegisterTransferData,
    ) -> Any:
        """This method calls each update of Message or CallbackQuery type."""
        db: Database = data['db']
        user = event.from_user

        if await db.user.user_register_check(active_user_id=user.id):
            if data['event_router'].name == 'start':
                return await data['bot'].send_message(user.id, "1. Посмотреть список желании\n2. Посмотреть профиль",
                                                      reply_markup=MENU_KEYBOARD)

        return await handler(event, data)
