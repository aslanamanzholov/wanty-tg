"""This file represents a Dreams logic."""
import logging
from os import getenv

import emoji
import requests

from aiogram import types
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from src.bot.structures.keyboards.dreams import (DREAMS_MAIN_BUTTONS_MARKUP, DREAMS_NOT_FOUND_BUTTONS_MARKUP,
                                                 CANCEL_BUTTON, CANCEL_WITHOUT_IMAGE_BUTTON,
                                                 CANCEL_WITHOUT_DETAILS_BUTTON)

from .router import dreams_router
from src.bot.structures.fsm.dream_create import DreamGroup
from src.bot.structures.fsm.register import RegisterGroup
from src.bot.structures.keyboards.menu import MENU_KEYBOARD


@dreams_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state is not None:
        await state.clear()
        await message.answer(f"Вы отменили {emoji.emojize(':smiling_face_with_tear:')}",
                             reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP)


@dreams_router.message(F.text.lower().startswith('создать желание'))
async def process_create_command(message: types.Message, state: FSMContext, db):
    user = await db.user.user_register_check(active_user_id=message.from_user.id)

    if user:
        await state.set_state(DreamGroup.name)
        return await message.answer(
            'Расскажите другим о ваших желаниях.\n(Например: "Хочу путешествовать по странам")',
            reply_markup=CANCEL_BUTTON,
        )
    else:
        await state.set_state(RegisterGroup.age)
        return await message.answer(
            'Для того чтобы создать желание, необходимо зарегистрироваться '
            f'{emoji.emojize(":upside-down_face:")}\nСколько вам лет?',
            reply_markup=CANCEL_BUTTON
        )


@dreams_router.message(DreamGroup.name)
async def register_gender_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DreamGroup.description)

    text = (
        "Отправьте изображение с желанием. "
        "Это поможет привлечь больше внимания и заинтересовать больше людей "
        f"{emoji.emojize(':thumbs_up:')} (не обязательное поле)"
    )

    await message.answer(text, reply_markup=CANCEL_WITHOUT_IMAGE_BUTTON)


@dreams_router.message(DreamGroup.description)
async def register_gender_handler(message: Message, state: FSMContext):
    await state.update_data(image=message.photo)
    await state.set_state(DreamGroup.image)

    text = 'Опиши ниже подробности желаний {emoji}'.format(emoji=emoji.emojize(":upside-down_face:"))
    await message.answer(text, reply_markup=CANCEL_WITHOUT_DETAILS_BUTTON)


@dreams_router.message(DreamGroup.image)
async def register_gender_handler(message: Message, state: FSMContext, db):
    data = await state.get_data()
    description = data.get('description', '')

    dream_image = None
    if message.photo:
        photo = message.photo[-1]
        photo_file = await message.bot.get_file(photo.file_id)
        photo_url = photo_file.file_path
        request_url = f"https://api.telegram.org/file/bot{getenv('BOT_TOKEN')}/{photo_url}"

        response = requests.get(request_url)
        if response.status_code == 200:
            dream_image = response.content

    await db.dream.new(
        user_id=message.from_user.id,
        username=message.from_user.username,
        image=dream_image,
        name=data.get('name', ''),
        description=description
    )

    await state.clear()
    await message.answer(
        'Ты успешно поделился своим желанием с пользователями Wanty. Ожидайте взаимных откликов.',
        reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP
    )


current_record = {}


async def dreams_view_func(dream, message, db):
    if not dream:
        text = f'Больше желаний нет {emoji.emojize(":confused_face:")}'
        await message.answer(text, reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP)
        return

    dream_user = await db.user.get_user_by_id(user_id=dream.user_id)
    user_gender = emoji.emojize(':man:') if dream_user and dream_user.gender == 'Мужчина' else emoji.emojize(':woman:')
    formatted_date = dream.created_at.strftime("%d.%m.%Y")

    text = (
        f"\n*Тема*: {dream.name}\n"
        f"*Описание*: {dream.description}\n"
        f"*Город*: {dream_user.country if dream_user else 'Другой'}\n"
        f"*Автор*: {dream_user.name if dream_user else 'Анонимный'} {user_gender}\n"
        f"*Дата создания*: {formatted_date}"
    )

    if dream.image:
        await message.bot.send_photo(
            message.chat.id,
            types.BufferedInputFile(dream.image, filename=f"user_photo_{dream.id}.png"),
            caption=text,
            reply_markup=DREAMS_MAIN_BUTTONS_MARKUP,
            parse_mode='MARKDOWN'
        )
    else:
        await message.answer(text, reply_markup=DREAMS_MAIN_BUTTONS_MARKUP, parse_mode='MARKDOWN')


@dreams_router.message(F.text.lower().startswith('желания'))
@dreams_router.message(Command(commands='dreams'))
async def process_dreams_handler(message: types.Message, state: FSMContext, db):
    user_id = message.from_user.id
    user = await db.user.user_register_check(active_user_id=user_id)

    if user:
        offset = current_record.get(user_id, 0)
        dream = await db.dream.get_dream(user_id=user_id, offset=offset)
        await dreams_view_func(dream=dream, message=message, db=db)
    else:
        await state.set_state(RegisterGroup.age)
        text = f'Для того чтобы посмотреть желания, необходимо зарегистрироваться {emoji.emojize(":upside-down_face:")}\nСколько тебе лет?'
        await message.answer(text, reply_markup=CANCEL_BUTTON)


async def send_notification_to_author(author_id, dream, message):
    try:
        notification_message = (
            f"Ваше желание {dream.name} было лайкнуто! {emoji.emojize(':thumbs_up:')}\n"
            f"Хотите узнать, кто выразил поддержку? {emoji.emojize(':smiling_face_with_smiling_eyes:')}"
        )

        callback_data = (
            f"{message.from_user.username or message.from_user.id} "
            f"{dream.username or dream.user_id} {message.chat.id} {dream.id}"
        )

        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Да', callback_data=f"share_contact {callback_data}"),
                    InlineKeyboardButton(text='Нет', callback_data=f"not_share_contact {callback_data}")
                ]
            ]
        )

        await message.bot.send_message(author_id, notification_message, reply_markup=reply_markup,
                                       parse_mode='MARKDOWN')

    except TelegramForbiddenError as e:
        logging.error(e)


@dreams_router.callback_query(F.data.startswith("share_contact" or "not_share_contact"))
async def share_contact_callback_handler(callback_query: CallbackQuery, db):
    try:
        data_parts = callback_query.data.split(' ')
        action = data_parts[0]
        liker_username_id, dream_username_id, chat_id, dream_id = data_parts[1:]

        if action == "share_contact":
            dream = await db.dream.get_dream_by_id(dream_id=dream_id)

            notification_message = (
                f"Вот его профиль в Telegram, выполняйте "
                f"ваши совместные желания: {emoji.emojize(':smiling_face_with_hearts:')}\n"
                f"https://t.me/{liker_username_id}"
            )
            notification_for_sender_message = (
                f"Это автор желания *{dream.name}*, выполняйте совместные желания: "
                f"{emoji.emojize(':smiling_face_with_hearts:')}\n"
                f"https://t.me/{dream_username_id}"
            )

            await callback_query.bot.send_message(chat_id, notification_for_sender_message,
                                                  reply_markup=MENU_KEYBOARD, parse_mode='MARKDOWN')

            await callback_query.message.bot.edit_message_reply_markup(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=None
            )

            await db.dream_liked_record.new(
                author_user_id=dream_username_id,
                author_username=dream_username_id,
                liked_user_id=liker_username_id,
                liked_username=liker_username_id,
                dream_name=dream.name,
                type_feedback="share_contact"
            )

            await callback_query.message.answer(notification_message, reply_markup=MENU_KEYBOARD,
                                                parse_mode='MARKDOWN')
        else:
            user_id = callback_query.from_user.id
            offset = current_record.get(user_id, 0)
            dream = await db.dream.get_dream(user_id=user_id, offset=offset)
            await dreams_view_func(dream=dream, message=callback_query.message, db=db)
    except TelegramForbiddenError as e:
        logging.error(e)


@dreams_router.message(F.text.lower() == emoji.emojize(":red_heart:"))
async def process_like_command(message: types.Message, db):
    user_id = message.from_user.id

    offset = current_record.get(user_id, 0)
    current_record[user_id] = offset + 1

    dream = await db.dream.get_dream(user_id=user_id, offset=offset)
    author_id = dream.user_id if dream else None

    if author_id:
        await send_notification_to_author(author_id, dream, message)

    await (
        db.dream_liked_record.new(
            author_user_id=author_id,
            liked_user_id=user_id,
            liked_username=message.from_user.username,
            dream_name=dream.name,
            type_feedback="liked"
        ))

    next_dream = await db.dream.get_dream(user_id=user_id, offset=offset + 1)
    await dreams_view_func(dream=next_dream, message=message, db=db)


@dreams_router.message(F.text.lower() == emoji.emojize(":thumbs_down:"))
async def process_dislike_command(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    current_record[user_id] = offset + 1

    next_dream = await db.dream.get_dream(user_id=user_id, offset=offset + 1)
    await dreams_view_func(dream=next_dream, message=message, db=db)


@dreams_router.message(F.text.lower() == emoji.emojize(":ZZZ:"))
async def process_sleep_command(message: types.Message, db):
    user = await db.user.user_register_check(active_user_id=message.from_user.id)

    user_name = user.name or message.from_user.first_name
    message_text = (
        f"Привет, *{user_name}*\n\n"
        "1. Просмотреть список желаний\n"
        "2. Просмотреть мои желания\n"
        "3. Изменить имя"
    )

    await message.answer(message_text, reply_markup=MENU_KEYBOARD, parse_mode="MARKDOWN")
