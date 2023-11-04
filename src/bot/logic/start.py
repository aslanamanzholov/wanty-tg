"""This file represents a start logic."""

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.bot.filters.register_filter import RegisterFilter
from src.bot.structures.fsm.menu import MENU_KEYBOARD
from src.bot.structures.fsm.register import RegisterGroup
from src.bot.structures.keyboards.register import REGISTER_START_CONFIRM

start_router = Router(name='start')


@start_router.message(CommandStart(), RegisterFilter())
async def start_handler(message: types.Message, state: FSMContext, db):
    user = await db.user.user_register_check(active_user_id=message.from_user.id)
    if user is None:
        await state.set_state(RegisterGroup.age)
        return await message.answer(
            'Будьте первым кто делится желаниями в Wanty.\nЯ помогу найти тебе пару для совместных желании.',
            reply_markup=REGISTER_START_CONFIRM)
    else:
        await message.answer(f"Привет, {user.name if user.name else message.from_user.first_name}!\n\n"
                             f"1. Посмотреть список желании\n2. Посмотреть твои желании", reply_markup=MENU_KEYBOARD)
