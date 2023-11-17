"""This file represents a Dreams logic."""
from os import getenv

import emoji
import requests

from aiogram import types
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.structures.keyboards.dreams import (DREAMS_MAIN_BUTTONS_MARKUP, SLEEP_BUTTONS_MARKUP,
                                                 DREAMS_NOT_FOUND_BUTTONS_MARKUP, CANCEL_BUTTON,
                                                 CANCEL_WITHOUT_IMAGE_BUTTON)

from .router import dreams_router
from src.bot.structures.fsm.dream_create import DreamGroup
from src.bot.structures.fsm.register import RegisterGroup
from src.bot.structures.keyboards.menu import MENU_KEYBOARD


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
async def process_create_command(message: types.Message, state: FSMContext, db):
    user = await db.user.user_register_check(active_user_id=message.from_user.id)
    if user:
        await state.set_state(DreamGroup.name)
        return await message.answer(
            'Расскажи людям про свои желания\n(н-р: - Хочу путешествовать по странам)', reply_markup=CANCEL_BUTTON,
        )
    else:
        await state.set_state(RegisterGroup.age)
        return await message.answer(f'Для того чтобы создать желание, необходимо зарегистрироваться '
                                    f'{emoji.emojize(":upside-down_face:")}\nСколько тебе лет?',
                                    reply_markup=ReplyKeyboardRemove())


@dreams_router.message(DreamGroup.name)
async def register_gender_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DreamGroup.description)
    return await message.answer(f"Отправьте изображение с желанием, оно поможет привлечь больше внимания и "
                                f"заинтересовать больше людей {emoji.emojize(':thumbs_up:')} (не обязательное поле)",
                                reply_markup=CANCEL_WITHOUT_IMAGE_BUTTON)


@dreams_router.message(DreamGroup.description)
async def register_gender_handler(message: Message, state: FSMContext):
    await state.update_data(image=message.photo)
    await state.set_state(DreamGroup.image)
    return await message.answer(
        f'Опиши ниже подробности желаний {emoji.emojize(":upside-down_face:")}', reply_markup=CANCEL_BUTTON
    )


@dreams_router.message(DreamGroup.image)
async def register_gender_handler(message: Message, state: FSMContext, db):
    data = await state.update_data(description=message.text)
    dream_image = data['image']
    if dream_image:
        photo = data['image'][-1]
        photo_file = await message.bot.get_file(photo.file_id)
        photo_url = photo_file.file_path
        request_url = f"https://api.telegram.org/file/bot{getenv('BOT_TOKEN')}/{photo_url}"
        response = requests.get(request_url)
        if response.status_code == 200:
            dream_image = response.content

    await db.dream.new(user_id=message.from_user.id,
                       username=message.from_user.username,
                       image=dream_image,
                       name=data['name'],
                       description=data['description'])

    await state.clear()
    return await message.answer(
        'Ты успешно поделился со своим желанием с пользователями Wanty..\n\nОжидайте взаимных откликов',
        reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP
    )


current_record = {}


async def dreams_view_func(dream, message, db):
    if dream:
        dream_user_id = dream.user_id
        dream_user = await db.user.get_user_by_id(user_id=dream_user_id)
        user_gender = emoji.emojize(':man:') if dream_user and dream_user.gender == 'Мужчина' else emoji.emojize(':woman:')
        text = (f"\n*Тема*: {dream.name}\n"
                f"*Описание*: {dream.description}\n"
                f"*Автор*: {dream_user.name if dream_user else 'Анонимный'} {user_gender}")
        if dream.image:
            await message.bot.send_photo(message.chat.id,
                                         types.BufferedInputFile(dream.image,
                                                                 filename=f"user_photo_{dream.id}.png"),
                                         caption=text,
                                         reply_markup=DREAMS_MAIN_BUTTONS_MARKUP,
                                         parse_mode='MARKDOWN')
        else:
            await message.answer(text, reply_markup=DREAMS_MAIN_BUTTONS_MARKUP, parse_mode='MARKDOWN')
    else:
        text = f'Больше желании нет {emoji.emojize(":confused_face:")}'
        await message.answer(text, reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP)


@dreams_router.message(F.text.lower().startswith('желании'))
@dreams_router.message(Command(commands='dreams'))
async def process_dreams_handler(message: types.Message, state: FSMContext, db):
    user_id = message.from_user.id
    user = await db.user.user_register_check(active_user_id=message.from_user.id)
    if user:
        offset = current_record.get(user_id, 0)
        dream = await db.dream.get_dream(user_id=message.from_user.id, offset=offset)
        return await dreams_view_func(dream=dream, message=message, db=db)
    else:
        await state.set_state(RegisterGroup.age)
        return await message.answer(f'Для того чтобы посмотреть желании, необходимо зарегистрироваться '
                                    f'{emoji.emojize(":upside-down_face:")}\nСколько тебе лет?',
                                    reply_markup=ReplyKeyboardRemove())


async def send_notification_to_author(author_id, dream, message):
    notification_message = (f"Ваше желание {dream.name} было лайкнуто! {emoji.emojize(':thumbs_up:')}\n"
                            f"Хотите узнать, кто выразил поддержку? {emoji.emojize(':smiling_face_with_smiling_eyes:')}")

    callback_data = (f"{message.from_user.username if message.from_user.username else message.from_user.id} "
                     f"{dream.username if dream.username else dream.user_id} {message.chat.id} {dream.id}")

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да', callback_data=f"share_contact {callback_data}"),
                InlineKeyboardButton(text='Нет', callback_data=f"not_share_contact {callback_data}")
            ]
        ]
    )
    await message.bot.send_message(author_id, notification_message, reply_markup=reply_markup, parse_mode='MARKDOWN')


@dreams_router.callback_query(F.data.startswith("share_contact" or "not_share_contact"))
async def share_contact_callback_handler(callback_query: types.CallbackQuery, db):
    if F.data.startswith("share_contact"):
        liker_username_id = callback_query.data.split(' ')[1]
        dream_username_id = callback_query.data.split(' ')[2]
        chat_id = callback_query.data.split(' ')[3]
        dream_id = callback_query.data.split(' ')[4]

        dream = await db.dream.get_dream_by_id(dream_id=dream_id)

        notification_message = (f"Вот его профиль в Telegram, выполняйте "
                                f"ваши совместные желания: {emoji.emojize(':smiling_face_with_hearts:')}\n"
                                f"*https://t.me/{liker_username_id}*")
        notification_for_sender_message = (f"Это автор желании *{dream.name}*, выполняйте совместные желания: "
                                           f"{emoji.emojize(':smiling_face_with_hearts:')}\n"
                                           f"*https://t.me/{dream_username_id}*")
        await callback_query.bot.send_message(chat_id, notification_for_sender_message,
                                              reply_markup=MENU_KEYBOARD, parse_mode='MARKDOWN')

        await callback_query.message.bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )

        await callback_query.message.answer(notification_message, reply_markup=ReplyKeyboardRemove(),
                                            parse_mode='MARKDOWN')
    else:
        user_id = callback_query.message.from_user.id
        offset = current_record.get(user_id, 0)
        dream = await db.dream.get_dream(user_id=callback_query.message.from_user.id, offset=offset)
        return await dreams_view_func(dream=dream, message=callback_query.message, db=db)


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

    user = await db.user.user_register_check(active_user_id=user_id)

    return await dreams_view_func(dream=next_dream, message=message, db=db)


@dreams_router.message(F.text.lower() == emoji.emojize(":thumbs_down:"))
async def process_dislike_command(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    current_record[user_id] = offset + 1
    dreams = await db.dream.get_dream(user_id=message.from_user.id, offset=offset + 1)
    return await dreams_view_func(dream=dreams, message=message, db=db)


@dreams_router.message(F.text.lower() == emoji.emojize(":ZZZ:"))
async def process_sleep_command(message: types.Message):
    await message.answer("Подождем пока кто то откликнется на ваши желания", reply_markup=SLEEP_BUTTONS_MARKUP)
