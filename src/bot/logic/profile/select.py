"""This file represents a My Profile logic."""

from aiogram import types, F
from aiogram.filters import Command

from .router import myprofile_router
from src.bot.structures.keyboards.profile import PROFILE_MAIN_BUTTONS_MARKUP, INLINE_BUTTON_PROFILE_EDIT_MARKUP


@myprofile_router.message(F.text.lower() == 'My Profile')
@myprofile_router.message(Command(commands='myprofile'))
async def myprofile_handler(message: types.Message, db):
    dreams_of_user = await db.dream.get_dreams_of_user(user_id=message.from_user.id)
    for dream in dreams_of_user:
        text = (f"<b>Название:</b> {dream.name.strip()}\n---------------------------------------"
                f"\nОписание: {dream.description.strip()}\n\n")
        await message.answer("<b>Вот такие у тебя желании:</b>\n\n" + text,
                             reply_markup=INLINE_BUTTON_PROFILE_EDIT_MARKUP, parse_mode='HTML')


@myprofile_router.callback_query(F.data == "edit_dream")
async def myprofile_edit_dream_callback_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Вы нажали на кнопку Изменить")


@myprofile_router.callback_query(F.data == "delete_dream")
async def myprofile_delete_dream_callback_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Вы нажали на кнопку Удалить")
