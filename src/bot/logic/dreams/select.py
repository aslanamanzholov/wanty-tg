"""This file represents a Dreams logic."""
import emoji
from aiogram import types
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.structures.keyboards.dreams import (DREAMS_MAIN_BUTTONS_MARKUP, SLEEP_BUTTONS_MARKUP,
                                                 DREAMS_NOT_FOUND_BUTTONS_MARKUP, CANCEL_BUTTON)

from .router import dreams_router
from src.bot.structures.fsm.dream_create import DreamGroup


@dreams_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Вы успешно отменили", reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP,
    )


@dreams_router.message(F.text.lower().startswith('создать желание'))
async def process_create_command(message: types.Message, state: FSMContext):
    await state.set_state(DreamGroup.name)
    return await message.answer(
        'Расскажи людям про свои желания\n(н-р: - Хочу путешествовать по странам)', reply_markup=CANCEL_BUTTON,
    )


@dreams_router.message(DreamGroup.name)
async def register_gender_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DreamGroup.description)
    return await message.answer(
        'Опиши ниже подробности желаний ;)', reply_markup=CANCEL_BUTTON
    )


@dreams_router.message(DreamGroup.description)
async def register_gender_handler(message: Message, state: FSMContext, db):
    data = await state.update_data(description=message.text)
    await db.dream.new(user_id=message.from_user.id,
                       name=data['name'],
                       description=data['description'])
    await state.clear()
    return await message.answer(
        'Ты успешно поделился со своим желанием с пользователями Wanty..\n\nОжидайте взаимных откликов',
        reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP
    )

current_record = {}


async def dreams_view_func(dream, message, user_id, offset):
    if dream:
        current_record[user_id] = offset + 1
        text = '<b>Список желании интересных людей:</b>' + '\n\n'
        text += (f"Название: {dream.name}\n---------------------------------------\n"
                 f"Описание: {dream.description}\n\n")
        await message.answer(text, reply_markup=DREAMS_MAIN_BUTTONS_MARKUP, parse_mode='HTML')
    else:
        text = 'Больше желании нет :('
        await message.answer(text, reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP)


@dreams_router.message(F.text.lower().startswith('желании'))
@dreams_router.message(Command(commands='dreams'))
async def process_dreams_handler(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    dream = await db.dream.get_dream(user_id=message.from_user.id, offset=offset)
    return await dreams_view_func(dream, message, user_id, offset)


@dreams_router.message(F.text.lower() == emoji.emojize(":red_heart:"))
async def process_like_command(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    dream = await db.dream.get_dream(user_id=message.from_user.id, offset=offset)
    return await dreams_view_func(dream, message, user_id, offset)


@dreams_router.message(F.text.lower() == emoji.emojize(":thumbs_down:"))
async def process_dislike_command(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    dreams = await db.dream.get_dream(offset=offset, user_id=message.from_user.id)
    return await dreams_view_func(dreams, message, user_id, offset)


@dreams_router.message(F.text.lower() == emoji.emojize(":ZZZ:"))
async def process_sleep_command(message: types.Message):
    await message.answer("Подождем пока кто то откликнется на ваши желания", reply_markup=SLEEP_BUTTONS_MARKUP)
