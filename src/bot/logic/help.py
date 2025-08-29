from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router(name='help')


@help_router.message(F.text == "💡 Помощь")
@help_router.message(Command(commands='help'))
async def help_handler(message: Message):
    """Show help menu."""
    help_text = (
        "💡 **Справка по Wanty** 💡\n\n"
        "**🚀 Основные команды:**\n"
        "/start - Запуск бота\n"
        "/help - Показать эту справку\n"
        "/dreams - Просмотр желаний\n"
        "/profile - Показать профиль\n\n"
        
        "**💭 Как использовать:**\n"
        "1. Просматривай желания других\n"
        "2. Ставь лайки понравившимся\n"
        "3. Создавай свои желания\n"
        "4. Получай достижения и очки\n\n"
        
        "**🏆 Система достижений:**\n"
        "• Создание желания: +15 очков\n"
        "• Получение лайка: +5 очков\n"
        "• Просмотр желаний: +1 очко\n\n"
        
        "**💡 Дополнительные функции:**\n"
        "Используй inline кнопки для доступа к достижениям, категориям и статистике!"
    )
    
    # Создаем inline клавиатуру для навигации по справке
    from src.bot.structures.keyboards.menu import ADDITIONAL_FEATURES_MARKUP
    
    await message.answer(
        help_text,
        reply_markup=ADDITIONAL_FEATURES_MARKUP,
        parse_mode="MARKDOWN"
    )



