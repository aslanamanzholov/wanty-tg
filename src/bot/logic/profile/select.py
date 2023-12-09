"""This file represents a My Profile logic."""
from os import getenv

import emoji
import requests
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from .router import myprofile_router
from src.bot.structures.fsm.dream_edit import DreamEditGroup
from src.bot.structures.keyboards.dreams import (DREAMS_NOT_FOUND_BUTTONS_PROFILE_MARKUP,
                                                 CANCEL_BUTTON, DREAMS_NOT_FOUND_BUTTONS_MARKUP,
                                                 CANCEL_WITHOUT_IMAGE_BUTTON)
from src.bot.structures.fsm.register import ChangeProfileName
from src.bot.structures.keyboards.menu import MENU_KEYBOARD


@myprofile_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
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


@myprofile_router.message(F.text.lower().startswith('изменить имя'))
async def dream_change_name_handler(message: types.Message, state: FSMContext):
    await state.set_state(ChangeProfileName.name)
    await message.answer(text="Введите имя на которую хотите поменять", reply_markup=ReplyKeyboardRemove(),
                         parse_mode='MARKDOWN')


@myprofile_router.message(ChangeProfileName.name)
async def edit_dream_name_handler(message: types.Message, state: FSMContext, db):
    data = await state.update_data(name=message.text)
    user = await db.user.get_user_by_id(message.from_user.id)
    user.name = data.get('name', None)
    await db.session.commit()
    await state.clear()
    return await message.answer(text=f"Вы успешно поменяли имя на *{message.text}*", reply_markup=MENU_KEYBOARD,
                                parse_mode='MARKDOWN')


@myprofile_router.message(F.text.lower() == 'мои желания')
@myprofile_router.message(Command(commands='mydreams'))
async def mydream_handler(message: types.Message, db):
    dreams_of_user = await db.dream.get_dreams_of_user(user_id=message.from_user.id)
    if dreams_of_user:
        for ind, dream in enumerate(dreams_of_user):
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Изменить', callback_data=f'edit_dream {dream.id}')],
                    [InlineKeyboardButton(text='Удалить', callback_data=f'delete_dream {dream.id}')]
                ]
            )
            text = (f"\n*Желание №{ind + 1}*\n\n"
                    f"*Тема*: {dream.name}\n"
                    f"*Описание*: {dream.description}\n\n")
            if dream.image:
                await message.bot.send_photo(message.chat.id,
                                             types.BufferedInputFile(dream.image,
                                                                     filename=f"user_photo_{dream.id}.png"),
                                             caption=text,
                                             reply_markup=reply_markup,
                                             parse_mode='MARKDOWN')
            else:
                await message.answer(text, reply_markup=reply_markup, parse_mode='MARKDOWN')

            return await message.answer(f"Вы также можете выбрать одно из следующих действий: "
                                        f"{emoji.emojize(':backhand_index_pointing_down:')}",
                                        reply_markup=MENU_KEYBOARD,
                                        parse_mode='MARKDOWN')
    else:
        return await message.answer("Упс, но у вас нет желании в Wanty :(\nВы сможете создать желание по кнопке ниже",
                                    reply_markup=DREAMS_NOT_FOUND_BUTTONS_PROFILE_MARKUP)


@myprofile_router.callback_query(F.data.startswith("edit_dream"))
async def myprofile_edit_dream_callback_handler(callback_query: types.CallbackQuery, state: FSMContext, db):
    dream_id = callback_query.data.split(' ')[1] or None
    await state.set_state(DreamEditGroup.name)
    await state.update_data(dream_id=dream_id)
    return await callback_query.message.answer(
        f'{emoji.emojize(":speech_balloon:")} Напиши как ты хочешь редактировать название желании:',
        reply_markup=CANCEL_BUTTON,
    )


@myprofile_router.message(DreamEditGroup.name)
async def edit_dream_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DreamEditGroup.image)
    return await message.answer(f"Отправьте изображение с желанием, оно поможет привлечь больше внимания и "
                                f"заинтересовать больше людей {emoji.emojize(':thumbs_up:')} (не обязательное поле)",
                                reply_markup=CANCEL_WITHOUT_IMAGE_BUTTON)


@myprofile_router.message(DreamEditGroup.image)
async def edit_dream_description_handler(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo)
    await state.set_state(DreamEditGroup.description)
    return await message.answer(
        'Опиши ниже подробности желаний на которую хочешь поменять ;)', reply_markup=CANCEL_BUTTON
    )


@myprofile_router.message(DreamEditGroup.description)
async def edit_user_dream_handler(message: types.Message, state: FSMContext, db):
    data = await state.update_data(description=message.text)
    dream = await db.dream.get_dream_by_id(int(data['dream_id']))
    dream_image = data['image']
    if dream_image:
        photo = data['image'][-1]
        photo_file = await message.bot.get_file(photo.file_id)
        photo_url = photo_file.file_path
        request_url = f"https://api.telegram.org/file/bot{getenv('BOT_TOKEN')}/{photo_url}"
        response = requests.get(request_url)
        if response.status_code == 200:
            dream_image = response.content
    dream.name = data['name']
    dream.image = dream_image
    dream.description = data['description']
    await db.session.commit()
    await state.clear()
    return await message.answer(
        '*Ты успешно обновил содержимое желании..\n\nОжидайте взаимных откликов*',
        reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP, parse_mode="MARKDOWN"
    )


@myprofile_router.callback_query(F.data.startswith("delete_dream"))
async def myprofile_delete_dream_callback_handler(callback_query: types.CallbackQuery, db):
    dream_id = callback_query.data.split(' ')[1] or None
    dream = await db.dream.get_dream_by_id(int(dream_id))
    if dream:
        await db.session.delete(dream)
        await db.session.commit()
        await callback_query.message.answer("*Желание успешно удалена*", parse_mode='MARKDOWN')
    else:
        await callback_query.message.answer("*Не могу найти желание :(*", parse_mode='MARKDOWN')
