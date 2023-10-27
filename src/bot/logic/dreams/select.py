"""This file represents a Dreams logic."""

from aiogram import types
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message

from src.bot.structures.keyboards.dreams import (DREAMS_MAIN_BUTTONS_MARKUP, SLEEP_BUTTONS_MARKUP,
                                                 DREAMS_NOT_FOUND_BUTTONS_MARKUP)

from src.db.repositories import DreamRepo
from .router import dreams_router
from src.bot.structures.fsm.dream_create import DreamGroup


async def dreams_view_func(dreams, message):
    if not dreams:
        text = 'Увы, не могу найти желании :('
        await message.answer(text, reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP)
    else:
        text = '<b>Список желании интересных людей:</b>' + '\n\n'
        for dream in dreams:
            text += f"Название: {dream.name}\nОписание: {dream.description}\n\n"
        await message.answer(text, reply_markup=DREAMS_MAIN_BUTTONS_MARKUP, parse_mode='HTML')


@dreams_router.message(F.text.lower() == 'dreams')
@dreams_router.message(Command(commands='dreams'))
async def process_dreams_handler(message: types.Message, db):
    dreams = await db.dream.get_list_of_dreams(user_id=message.from_user.id)
    return await dreams_view_func(dreams, message)


@dreams_router.message(F.text.lower() == 'create')
async def process_create_command(message: types.Message, state: FSMContext):
    await state.set_state(DreamGroup.name)
    return await message.answer(
        'Расскажи людям про свои желания\n(н-р: - Хочу путешествовать по странам)', reply_markup=ReplyKeyboardRemove(),
    )


@dreams_router.message(DreamGroup.name)
async def register_gender_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DreamGroup.description)
    return await message.answer(
        'Опиши ниже подробности желаний ;)', reply_markup=ReplyKeyboardRemove()
    )


@dreams_router.message(DreamGroup.description)
async def register_gender_handler(message: Message, state: FSMContext, db):
    data = await state.update_data(description=message.text)
    await db.dream.new(user_id=message.from_user.id,
                       name=data['name'],
                       description=data['description'])
    await state.clear()
    return await message.answer(
        'Поздравляю, ты поделился с пользователями со своими желаниями..',
        reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP
    )


@dreams_router.message(F.text.lower() == 'like')
async def process_like_command(message: types.Message, db):
    pages_count = await db.dream.get_list_of_dreams(user_id=message.from_user.id)
    dreams = await db.dream.get_next_obj_of_dream(user_id=message.from_user.id)
    return await dreams_view_func(dreams, message)


@dreams_router.message(F.text.lower() == 'dislike')
async def process_dislike_command(message: types.Message, db):
    offset = 0
    if offset:
        offset += 1
    dreams = await db.dream.get_next_obj_of_dream(offset=offset, user_id=message.from_user.id)
    return await dreams_view_func(dreams, message)


@dreams_router.message(F.text.lower() == 'sleep')
async def process_sleep_command(message: types.Message):
    await message.answer("Подождем пока кто то откликнется на ваши желания", reply_markup=SLEEP_BUTTONS_MARKUP)
