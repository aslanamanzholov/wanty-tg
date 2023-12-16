"""This file represents a start logic."""

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.bot.structures.keyboards.profile import INLINE_BUTTON_TG_CHANNEL_URL_MARKUP
from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.bot.filters.register_filter import RegisterFilter
from src.bot.structures.fsm.register import RegisterGroup
from src.bot.structures.keyboards.register import REGISTER_START_CONFIRM

start_router = Router(name='start')


@start_router.message(CommandStart(), RegisterFilter())
async def start_handler(message: types.Message, state: FSMContext, db):
    user = await db.user.user_register_check(active_user_id=message.from_user.id)

    if user is None:
        await state.set_state(RegisterGroup.age)

        introduction_text = (
            "1. **Здравствуй, новый пользователь!**\n"
            "   Добро пожаловать в наш телеграмм-бот! Мы рады видеть тебя здесь.\n\n"
            "2. **Ознакомься с функцией \"Желания\":**\n"
            "   Для просмотра желания, жми на кнопку \"Желания ☁️\". После этого появится список желаний, "
            "   созданных другими пользователями.\n\n"
            "3. **Обзор желаний:**\n"
            "   Пролистай список и посмотри, что другие пользователи хотят. Например, кто-то может хотеть провести "
            "   время весело и интересно.\n\n"
            "4. **Выражай свои предпочтения:**\n"
            "   Если ты также хочешь чего-то подобного, просто нажми на кнопку ❤️ ниже желания. Таким образом, "
            "   ты выражаешь свою заинтересованность в этом желании.\n\n"
            "5. **Ожидай подтверждения:**\n"
            "   Автор желания увидит, что ты заинтересован в его/ее желании. Если он/она подтвердит, то ты "
            "   сможешь увидеть его/ее профиль и, возможно, встретиться для совместного времяпрепровождения.\n\n"
            "6. **Профиль и общение:**\n"
            "   После подтверждения ты сможешь посмотреть профиль автора и начать общение, чтобы договориться о "
            "   встрече или активности.\n\n"
            "7. **Не забывай быть активным:**\n"
            "   Желаем тебе приятного времяпрепровождения в нашем боте! Не стесняйся выражать свои интересы и "
            "   находить единомышленников.\n\n"
            "   Приятного общения! ☁️❤️\n\n"
            "   *Это телеграм-канал моего создателя:*"
        )

        await message.answer(introduction_text, reply_markup=INLINE_BUTTON_TG_CHANNEL_URL_MARKUP, parse_mode="MARKDOWN")
        await message.answer('*Для начала, нажми на кнопку ниже:*', reply_markup=REGISTER_START_CONFIRM, parse_mode="MARKDOWN")
    else:
        user_greeting_text = f"Привет, **{user.name if user.name else message.from_user.first_name}**!\n\n" \
                             "1. Просмотреть список желаний\n" \
                             "2. Просмотреть мои желания\n" \
                             "3. Изменить имя"

        await message.answer(user_greeting_text, reply_markup=MENU_KEYBOARD, parse_mode="MARKDOWN")
