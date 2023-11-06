"""This file represents a Dreams logic."""
import json

import emoji
from aiogram import types
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.structures.keyboards.dreams import (DREAMS_MAIN_BUTTONS_MARKUP, SLEEP_BUTTONS_MARKUP,
                                                 DREAMS_NOT_FOUND_BUTTONS_MARKUP, CANCEL_BUTTON,
                                                 DREAMS_CALLBACK_FROM_USER_BUTTONS_MARKUP)

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
        "Вы отменили :(", reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP,
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
                       username=message.from_user.username,
                       name=data['name'],
                       description=data['description'])
    await state.clear()
    return await message.answer(
        'Ты успешно поделился со своим желанием с пользователями Wanty..\n\nОжидайте взаимных откликов',
        reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP
    )


current_record = {}


async def dreams_view_func(dream, message):
    if dream:
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
    return await dreams_view_func(dream, message)


async def send_notification_to_author(author_id, dream, message):
    notification_message = (f"Ваше желание <b>{dream.name}</b> получило лайк.\n"
                            f"Хотите узнать, кто это сделал?")

    callback_data = f"{message.from_user.username if message.from_user.username else message.from_user.id} {dream.username if dream.username else dream.user_id} {message.chat.id}"

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да', callback_data=f"share_contact {callback_data}"),
                InlineKeyboardButton(text='Нет', callback_data=f"not_share_contact {callback_data}")
            ]
        ]
    )
    await message.bot.send_message(author_id, notification_message, reply_markup=reply_markup, parse_mode='HTML')


@dreams_router.callback_query(F.data.startswith("share_contact" or "not_share_contact"))
async def share_contact_callback_handler(callback_query: types.CallbackQuery, db):
    if F.data.startswith("share_contact"):
        liker_username_id = callback_query.data.split(' ')[1]
        dream_username_id = callback_query.data.split(' ')[2]
        chat_id = callback_query.data.split(' ')[3]

        notification_message = (f"Вот его профиль в телеграмме, выполняйте "
                                f"ваши совместные желания:\n"
                                f"<a href='https://t.me/{liker_username_id}/'>{liker_username_id}</a>")
        notification_for_sender_message = (f"Это автор желании, выполняйте совместные желания:\n"
                                           f"<a href='https://t.me/{dream_username_id}/'>{dream_username_id}</a>")
        await callback_query.bot.send_message(chat_id, notification_for_sender_message,
                                              reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')

        return await callback_query.message.answer(notification_message, reply_markup=ReplyKeyboardRemove(),
                                                   parse_mode='HTML')
    else:
        user_id = callback_query.message.from_user.id
        offset = current_record.get(user_id, 0)
        dream = await db.dream.get_dream(user_id=callback_query.message.from_user.id, offset=offset)
        return await dreams_view_func(dream, callback_query.message)


@dreams_router.message(F.text.lower() == emoji.emojize(":red_heart:"))
async def process_like_command(message: types.Message, db):
    user_id = message.from_user.id

    offset = current_record.get(user_id, 0)

    current_record[user_id] = offset + 1

    dream = await db.dream.get_dream(user_id=message.from_user.id, offset=offset)

    author_id = dream.user_id if dream else None
    if author_id:
        await send_notification_to_author(author_id, dream, message)

    next_dream = await db.dream.get_dream(user_id=message.from_user.id, offset=offset + 1)

    return await dreams_view_func(next_dream, message)


@dreams_router.message(F.text.lower() == emoji.emojize(":thumbs_down:"))
async def process_dislike_command(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    current_record[user_id] = offset + 1
    dreams = await db.dream.get_dream(user_id=message.from_user.id, offset=offset + 1)
    return await dreams_view_func(dreams, message)


@dreams_router.message(F.text.lower() == emoji.emojize(":ZZZ:"))
async def process_sleep_command(message: types.Message):
    await message.answer("Подождем пока кто то откликнется на ваши желания", reply_markup=SLEEP_BUTTONS_MARKUP)
