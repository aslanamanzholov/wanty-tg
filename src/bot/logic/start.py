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
        await message.answer(
            text="1. *Здравствуй, новый пользователь!*\nДобро пожаловать в наш телеграмм-бот! Мы рады видеть тебя "
                 "здесь.\n\n2. *Ознакомься с функцией \"Желания\":*\nДля просмотра желания, жми на кнопку "
                 "\"Желания ☁️\". После этого появится список желаний, созданных другими пользователями.\n\n3. "
                 "*Обзор желаний:*\nПролистай список и посмотри, что другие пользователи хотят. Например, кто-то может "
                 "хотеть провести время весело и интересно.\n\n4. *Выражай свои предпочтения:*\nЕсли ты также хочешь "
                 "чего-то подобного, просто нажми на кнопку ❤️ ниже желания. Таким образом, ты выражаешь свою "
                 "заинтересованность в этом желаний.\n\n5. *Ожидай подтверждения:*\nАвтор желания увидит, что ты "
                 "заинтересован в его/ее желании. Если он/она подтвердит, то ты сможешь увидеть его/ее профиль и, "
                 "возможно, встретиться для совместного времяпрепровождения.\n\n6. *Профиль и общение:*\nПосле "
                 "подтверждения ты сможешь посмотреть профиль автора и начать общение, чтобы договориться о встрече "
                 "или активности.\n\n7. *Не забывай быть активным:*\nЖелаем тебе приятного времяпрепровождения в нашем "
                 "боте! Не стесняйся выражать свои интересы и находить единомышленников."
                 "\n\nПриятного общения! ☁️❤️\n\n*Это телеграм-канал моего создателя:*",
            reply_markup=INLINE_BUTTON_TG_CHANNEL_URL_MARKUP,
            parse_mode="MARKDOWN"
        )
        return await message.answer(
            '*Для начала, нажмите на кнопку ниже:*',
            reply_markup=REGISTER_START_CONFIRM, parse_mode="MARKDOWN")
    else:
        return await message.answer(f"Привет, *{user.name if user.name else message.from_user.first_name}*!\n\n"
                                    f"1. Просмотреть список желаний\n2. Просмотреть мои желания\n3. Изменить имя",
                                    reply_markup=MENU_KEYBOARD, parse_mode="MARKDOWN")
