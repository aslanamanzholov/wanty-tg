"""This file represents a start logic."""

from aiogram import Router, types, F
from aiogram.filters import Command

from aiogram.utils.keyboard import (ReplyKeyboardBuilder, ReplyKeyboardMarkup, InlineKeyboardBuilder,
                                    InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton, KeyboardButtonPollType)

from .router import myprofile_router


@myprofile_router.message(F.text == 'My profile')
@myprofile_router.message(Command(commands='myprofile'))
async def myprofile_handler(message: types.Message):
    menu_builder = ReplyKeyboardBuilder()

    menu_builder.add(
        KeyboardButton(text="Список желании")
    )

    menu_builder.add(
        KeyboardButton(text="Написать желания")
    )

    await message.answer(
        'Вот такие у тебя желании:',
        reply_markup=menu_builder.as_markup(resize_keyboard=True)
    )
