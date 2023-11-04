"""This file represents a My Profile logic."""

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .router import myprofile_router
from src.bot.structures.fsm.dream_edit import DreamEditGroup
from src.bot.structures.keyboards.dreams import (DREAMS_NOT_FOUND_BUTTONS_PROFILE_MARKUP,
                                                 CANCEL_BUTTON, DREAMS_NOT_FOUND_BUTTONS_MARKUP)


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


@myprofile_router.message(F.text.lower() == 'мои желании')
@myprofile_router.message(Command(commands='mydreams'))
async def mydream_handler(message: types.Message, db):
    dreams_of_user = await db.dream.get_dreams_of_user(user_id=message.from_user.id)
    if dreams_of_user:
        for dream in dreams_of_user:
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Изменить', callback_data=f'edit_dream {dream.id}')],
                    [InlineKeyboardButton(text='Удалить', callback_data=f'delete_dream {dream.id}')]
                ]
            )
            text = (f"<b>Название:</b> {dream.name.strip()}\n---------------------------------------"
                    f"\n<b>Описание:</b> {dream.description.strip()}\n\n")
            await message.answer("<b>Вот такие у тебя желании:</b>\n\n" + text,
                                 reply_markup=reply_markup, parse_mode='HTML')
    else:
        await message.answer("Упс, но у вас нет желании в Wanty :(\nВы сможете создать желание по кнопке ниже",
                             reply_markup=DREAMS_NOT_FOUND_BUTTONS_PROFILE_MARKUP)


@myprofile_router.callback_query(F.data.startswith("edit_dream"))
async def myprofile_edit_dream_callback_handler(callback_query: types.CallbackQuery, state: FSMContext, db):
    dream_id = callback_query.data.split(' ')[1] or None
    await state.set_state(DreamEditGroup.name)
    await state.update_data(dream_id=dream_id)
    return await callback_query.message.answer(
        'Напиши как ты хочешь редактировать название желании:', reply_markup=CANCEL_BUTTON,
    )


@myprofile_router.message(DreamEditGroup.name)
async def edit_dream_description_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DreamEditGroup.description)
    return await message.answer(
        'Опиши ниже подробности желаний на которую хочешь поменять ;)', reply_markup=CANCEL_BUTTON
    )


@myprofile_router.message(DreamEditGroup.description)
async def edit_user_dream_handler(message: types.Message, state: FSMContext, db):
    data = await state.update_data(description=message.text)
    dream = await db.dream.get_dream_by_id(int(data['dream_id']))
    dream.data = data
    db.session.commit()
    await state.clear()
    return await message.answer(
        'Ты успешно обновил содержимое желании..\n\nОжидайте взаимных откликов',
        reply_markup=DREAMS_NOT_FOUND_BUTTONS_MARKUP
    )


@myprofile_router.callback_query(F.data.startswith("delete_dream"))
async def myprofile_delete_dream_callback_handler(callback_query: types.CallbackQuery, db):
    dream_id = callback_query.data.split(' ')[1] or None
    dream = await db.dream.get_dream_by_id(int(dream_id))
    if dream:
        await db.session.delete(dream)
        await db.session.commit()
        await callback_query.message.edit_text("Желание успешно удалена")
    else:
        await callback_query.message.edit_text("Не могу найти желание :(")
