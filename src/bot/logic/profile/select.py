"""This file represents a My Profile logic."""

from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.db.models import Dream
from .router import myprofile_router
from src.bot.structures.keyboards.profile import INLINE_BUTTON_PROFILE_EDIT_MARKUP


@myprofile_router.message(F.text.lower() == 'my profile')
@myprofile_router.message(Command(commands='myprofile'))
async def myprofile_handler(message: types.Message, db):
    dreams_of_user = await db.dream.get_dreams_of_user(user_id=message.from_user.id)
    for dream in dreams_of_user:
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Изменить', callback_data=f'edit_dream {dream.id}')],
                [InlineKeyboardButton(text='Удалить', callback_data=f'delete_dream {dream.id}')]
            ]
        )
        text = (f"<b>Название:</b> {dream.name.strip()}\n---------------------------------------"
                f"\nОписание: {dream.description.strip()}\n\n")
        await message.answer("<b>Вот такие у тебя желании:</b>\n\n" + text,
                             reply_markup=reply_markup, parse_mode='HTML')


@myprofile_router.callback_query(F.data.startswith("edit_dream"))
async def myprofile_edit_dream_callback_handler(callback_query: types.CallbackQuery, db):
    await callback_query.message.answer("Вы нажали на кнопку Изменить")


@myprofile_router.callback_query(F.data.startswith("delete_dream"))
async def myprofile_delete_dream_callback_handler(callback_query: types.CallbackQuery, db):
    dream_id = callback_query.data.split(' ')[1] or None
    if dream_id:
        await db.dream.delete_dream_of_user(int(dream_id))
    await callback_query.message.edit_text("Желание успешно удален")
