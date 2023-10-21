from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F

from src.bot.structures.keyboards.dreams import (DREAMS_MAIN_BUTTONS_MARKUP, LIKE_DISLIKE_BUTTONS_MARKUP,
                                                 SLEEP_BUTTONS_MARKUP)
from .router import dreams_router


@dreams_router.message(F.text == 'Dreams')
@dreams_router.message(Command(commands='dreams'))
async def dreams_handler(message: types.Message):
    dreams = [
        {
            "name": "Хочу полететь в Дубай",
            "users_count": 10,
            "author": "Amanzholov Aslan"
        },
        {
            "name": "Хочу научится английскому языку",
            "users_count заинтересованных": 4,
            "author": "Jason Statham"
        }
    ]

    text = 'Список желании интересных людей:' + '\n\n'
    for dream in dreams:
        for name, value in dream.items():
            text += f'{name} - {value}\n'
    await message.answer(text, reply_markup=DREAMS_MAIN_BUTTONS_MARKUP)


@dreams_router.message(F.text == 'Like')
async def process_like_command(message: types.Message):
    await message.answer("You liked", reply_markup=LIKE_DISLIKE_BUTTONS_MARKUP)


@dreams_router.message(F.text == 'Dislike')
async def process_dislike_command(message: types.Message):
    await message.answer("You disliked", reply_markup=LIKE_DISLIKE_BUTTONS_MARKUP)


@dreams_router.message(F.text == 'Sleep')
async def process_sleep_command(message: types.Message):
    await message.answer("Подождем пока кто то откликнется на ваши желания", reply_markup=SLEEP_BUTTONS_MARKUP)
