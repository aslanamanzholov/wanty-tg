from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command

from .router import register_router
from src.bot.structures.fsm.register import RegisterGroup
from src.bot.structures.keyboards.register import REGISTER_USER_COUNTRY, REGISTER_USER_GENDER, REGISTER_SUCCESS_MARKUP, \
    REGISTER_START_CONFIRM


@register_router.message(F.text == 'ok, давай начнем')
async def register_confirmation(message: Message, state: FSMContext):
    await state.set_state(RegisterGroup.age)
    return await message.answer(
        'Сколько тебе лет?', reply_markup=ReplyKeyboardRemove(),
    )


@register_router.message(Command("cancel"))
@register_router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Вы отменили регистрацию", reply_markup=REGISTER_START_CONFIRM,
    )


@register_router.message(RegisterGroup.age)
async def register_confirmation(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(RegisterGroup.gender)
    return await message.answer(
        'Теперь определимся с полом', reply_markup=REGISTER_USER_GENDER
    )


@register_router.message(RegisterGroup.gender)
async def register_confirmation(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(RegisterGroup.country)
    return await message.answer(
        'Из какого ты города?', reply_markup=REGISTER_USER_COUNTRY
    )


@register_router.message(RegisterGroup.country)
async def register_confirmation(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await state.set_state(RegisterGroup.name)
    return await message.answer(
        'Как мне тебя называть?', reply_markup=ReplyKeyboardRemove()
    )


@register_router.message(RegisterGroup.name)
async def register_confirmation(message: Message, state: FSMContext):
    data = await state.update_data(name=message.text)
    await state.clear()
    return await message.answer(
        f'Поздравляю с успешной регистрацией {data["name"]}', reply_markup=REGISTER_SUCCESS_MARKUP
    )
