"""Improved start logic with better UX and onboarding."""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.bot.structures.keyboards.dreams import DREAMS_NOT_FOUND_INLINE_MARKUP
from src.bot.structures.keyboards.profile import INLINE_BUTTON_TG_CHANNEL_URL_MARKUP
from src.bot.filters.register_filter import RegisterFilter
from src.bot.structures.fsm.register import RegisterGroup
from src.bot.structures.keyboards.register import REGISTER_START_CONFIRM

start_router = Router(name='start')


@start_router.message(Command("start"), RegisterFilter())
async def start_handler(message: types.Message, state: FSMContext, db):
    """Improved start handler with better UX."""
    user = await db.user.user_register_check(active_user_id=message.from_user.id)

    if user is None:
        # Новый пользователь - показываем улучшенный onboarding
        await state.set_state(RegisterGroup.age)
        
        # Краткое приветствие
        welcome_text = (
            "🌟 **Добро пожаловать в Wanty!** 🌟\n\n"
            "Место, где желания сбываются вместе!\n\n"
            "Этот бот поможет тебе найти единомышленников и воплотить в жизнь "
            "самые интересные желания."
        )
        
        await message.answer(
            welcome_text, 
            reply_markup=INLINE_BUTTON_TG_CHANNEL_URL_MARKUP, 
            parse_mode="MARKDOWN"
        )
        
        # Показываем первый шаг onboarding
        step1_text = (
            "📝 **Регистрация**\n\n"
            "Для начала работы с ботом нужно немного рассказать о себе.\n\n"
            "**Сколько тебе лет?**\n"
            "💡 Введи свой возраст цифрами"
        )
        
        await message.answer(
            step1_text, 
            reply_markup=REGISTER_START_CONFIRM, 
            parse_mode="MARKDOWN"
        )
        
        # Показываем быстрые действия
        await message.answer(
            "🚀 **Быстрый старт**\n"
            "Пока ты регистрируешься, можешь посмотреть, что у нас есть:\n\n"
            "**🎯 Что ждет тебя:**\n"
            "• 🏆 Система достижений за активностью\n"
            "• 📂 Категории желаний по интересам\n"
            "• 📊 Статистика активности\n"
            "• 🤝 Поиск единомышленников",
            reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
            parse_mode="MARKDOWN"
        )
        
    else:
        # Возвращающийся пользователь - показываем персонализированное меню
        user_name = user.name if user.name else message.from_user.first_name
        
        welcome_back_text = (
            "🎉 **С возвращением!** 🎉\n\n"
            f"Привет, **{user_name}**! 👋\n\n"
            "Рад снова тебя видеть! Готов продолжить поиск интересных желаний?\n\n"
            "**🚀 Новые возможности:**\n"
            "• 🏆 Система достижений и очков\n"
            "• 📂 Категории желаний по интересам\n"
            "• 📊 Подробная статистика активности\n\n"
            "**Что будем делать сегодня?** 🎯"
        )
        
        await message.answer(
            welcome_back_text, 
            reply_markup=MENU_KEYBOARD, 
            parse_mode="MARKDOWN"
        )
        
        # Отправляем inline кнопки для дополнительных функций
        from src.bot.structures.keyboards.menu import ADDITIONAL_FEATURES_MARKUP
        
        await message.answer(
            "🔧 **Дополнительные возможности:**",
            reply_markup=ADDITIONAL_FEATURES_MARKUP,
            parse_mode="MARKDOWN"
        )
        
        # Показываем полезные советы
        await message.answer(
            "💡 **Совет дня:**\n"
            "Регулярно просматривай новые желания - возможно, именно сегодня "
            "появится то, что ты искал! ✨"
        )



