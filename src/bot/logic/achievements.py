"""Achievements router for Wanty bot."""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.structures.keyboards.menu import MENU_KEYBOARD, ADDITIONAL_FEATURES_MARKUP
from src.bot.structures.keyboards.dreams import CATEGORIES_MARKUP
from src.bot.structures.achievements import achievement_system
from src.bot.structures.dream_categories import category_system

import logging

achievements_router = Router(name='achievements')


@achievements_router.message(Command(commands='achievements'))
@achievements_router.message(F.text == "🏆 Достижения")
async def achievements_handler(message: types.Message, db):
    """Show user achievements and progress."""
    user_id = message.from_user.id
    
    user = await db.user.user_register_check(active_user_id=user_id)
    
    if not user:
        logging.warning(f"User {user_id} not found in database")
        await message.answer(
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для просмотра достижений нужно сначала зарегистрироваться.",
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )
        return
    
    # Получаем реальную статистику пользователя из БД
    user_progress = await db.progress.get_user_progress(user_id)
    if not user_progress:
        # Если прогресса нет, создаем запись
        user_progress = await db.progress.create_user_progress(user_id)
    
    user_stats = {
        "total_dreams": user_progress.total_dreams,
        "total_likes_received": user_progress.total_likes_received,
        "total_dreams_viewed": user_progress.total_dreams_viewed,
        "total_likes_given": user_progress.total_likes_given,
        "consecutive_days": user_progress.consecutive_days,
        "users_helped": user_progress.users_helped
    }
    
    # Получаем прогресс по достижениям
    progress = achievement_system.get_user_progress(user_stats)
    
    # Подсчитываем статистику
    unlocked_count = sum(1 for p in progress.values() if p["is_unlocked"])
    total_count = len(progress)
    total_points = sum(p["achievement"].points for p in progress.values() if p["is_unlocked"])
    
    achievements_text = (
        f"🏆 **Достижения {user.name}** 🏆\n\n"
        f"**📊 Общая статистика:**\n"
        f"• Разблокировано: **{unlocked_count}/{total_count}**\n"
        f"• Общие очки: **{user_progress.total_points}**\n"
        f"• Прогресс: **{round((unlocked_count/total_count)*100, 1)}%**\n\n"
        
        "**🌟 Твои достижения:**\n"
    )
    
    # Показываем разблокированные достижения
    unlocked_achievements = [p for p in progress.values() if p["is_unlocked"]]
    if unlocked_achievements:
        for progress_data in unlocked_achievements:
            achievement = progress_data["achievement"]
            achievements_text += (
                f"{achievement.emoji} **{achievement.name}** - {achievement.points} очков\n"
                f"   {achievement.description}\n\n"
            )
    else:
        achievements_text += "Пока нет разблокированных достижений.\n\n"
    
    # Показываем ближайшие достижения
    locked_achievements = [p for p in progress.values() if not p["is_unlocked"]]
    if locked_achievements:
        achievements_text += "**🎯 Ближайшие цели:**\n"
        for progress_data in locked_achievements[:3]:  # Показываем только 3 ближайших
            achievement = progress_data["achievement"]
            current = progress_data["current_value"]
            required = progress_data["required_value"]
            percentage = progress_data["progress_percentage"]
            
            achievements_text += (
                f"{achievement.emoji} **{achievement.name}**\n"
                f"   Прогресс: {current}/{required} ({percentage:.1f}%)\n"
                f"   {achievement.requirement}\n\n"
            )
    
    achievements_text += "**💡 Совет:** Будь активным, чтобы разблокировать больше достижений!"
    
    await message.answer(
        achievements_text,
        reply_markup=MENU_KEYBOARD,
        parse_mode="MARKDOWN"
    )


@achievements_router.message(Command(commands='categories'))
@achievements_router.message(F.text == "📂 Категории")
async def categories_handler(message: types.Message):
    """Show dream categories."""
    categories = category_system.get_all_categories()
    
    categories_text = (
        "📂 **Категории желаний** 📂\n\n"
        "Выбери интересующую тебя категорию для просмотра желаний:\n\n"
    )
    
    for category in categories:
        categories_text += (
            f"{category.emoji} **{category.name}**\n"
            f"   {category.description}\n\n"
        )
    
    categories_text += "**💡 Как использовать:**\n"
    categories_text += "• Нажми на категорию для просмотра желаний\n"
    categories_text += "• Создавай желания в подходящих категориях\n"
    categories_text += "• Ищи единомышленников по интересам"
    
    await message.answer(
        categories_text,
        reply_markup=CATEGORIES_MARKUP,
        parse_mode="MARKDOWN"
    )


@achievements_router.message(F.text == "📂 Категории")
async def categories_text_handler(message: types.Message):
    """Handle categories button press."""
    await categories_handler(message)


@achievements_router.message(F.text == "🔙 Назад к желаниям")
async def back_to_dreams_handler(message: types.Message):
    """Return to dreams main menu."""
    back_text = (
        "🔙 **Возвращаемся к желаниям** 🔙\n\n"
        "Теперь ты снова в главном меню просмотра желаний.\n\n"
        "**💡 Что можно сделать:**\n"
        "• Просматривать желания\n"
        "• Ставить лайки/дизлайки\n"
        "• Создавать свои желания\n"
        "• Начинать сначала"
    )
    
    # Показываем кнопки для просмотра желаний
    from src.bot.structures.keyboards.dreams import DREAMS_MAIN_INLINE_MARKUP
    
    await message.answer(
        back_text,
        reply_markup=DREAMS_MAIN_INLINE_MARKUP,
        parse_mode="MARKDOWN"
    )


@achievements_router.callback_query(lambda c: c.data.startswith("cat_"))
async def category_callback(callback_query: types.CallbackQuery):
    """Handle category selection."""
    category_id = callback_query.data.replace("cat_", "")
    category = category_system.get_category(category_id)
    
    if not category:
        await callback_query.answer("Категория не найдена")
        return
    
    await callback_query.answer(f"Категория: {category.name}")
    
    # Получаем примеры желаний для категории
    examples = category_system.get_random_examples(category_id, 3)
    
    category_text = (
        f"{category.emoji} **{category.name}** {category.emoji}\n\n"
        f"**📝 Описание:**\n{category.description}\n\n"
        "**💭 Примеры желаний:**\n"
    )
    
    for example in examples:
        category_text += f"• {example}\n"
    
    category_text += f"\n**🔍 Хочешь посмотреть желания в этой категории?**\n"
    category_text += "Используй кнопки ниже для навигации!"
    
    # Показываем кнопки для навигации по категориям
    from src.bot.structures.keyboards.dreams import CATEGORIES_MARKUP
    
    await callback_query.message.answer(
        category_text,
        reply_markup=CATEGORIES_MARKUP,
        parse_mode="MARKDOWN"
    )


@achievements_router.message(Command(commands='stats'))
@achievements_router.message(F.text == "📊 Статистика")
async def stats_handler(message: types.Message, db):
    """Show user statistics."""
    user_id = message.from_user.id
    
    user = await db.user.user_register_check(active_user_id=user_id)
    
    if not user:
        logging.warning(f"User {user_id} not found in database")
        await message.answer(
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для просмотра статистики нужно сначала зарегистрироваться.",
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )
        return
    
    # Получаем реальную статистику пользователя из БД
    user_progress = await db.progress.get_user_progress(user_id)
    if not user_progress:
        # Если прогресса нет, создаем запись
        user_progress = await db.progress.create_user_progress(user_id)
    
    user_stats = {
        "total_dreams": user_progress.total_dreams,
        "total_likes_received": user_progress.total_likes_received,
        "total_dreams_viewed": user_progress.total_dreams_viewed,
        "total_likes_given": user_progress.total_likes_given,
        "consecutive_days": user_progress.consecutive_days,
        "users_helped": user_progress.users_helped
    }
    
    stats_text = (
        f"📊 **Статистика {user.name}** 📊\n\n"
        f"**🎯 Созданные желания:**\n"
        f"• Всего создано: **{user_stats['total_dreams']}**\n"
        f"• Получено лайков: **{user_stats['total_likes_received']}**\n"
        f"• Средний рейтинг: **{round(user_stats['total_likes_received'] / max(user_stats['total_dreams'], 1), 1)}**\n\n"
        
        f"**👀 Активность:**\n"
        f"• Просмотрено желаний: **{user_stats['total_dreams_viewed']}**\n"
        f"• Поставлено лайков: **{user_stats['total_likes_given']}**\n"
        f"• Дней подряд: **{user_stats['consecutive_days']}**\n\n"
        
        f"**🏆 Достижения:**\n"
        f"• Общие очки: **{user_progress.total_points}**\n\n"
        
        f"**🤝 Взаимодействие:**\n"
        f"• Помог пользователям: **{user_stats['users_helped']}**\n\n"
        
        "**💡 Рекомендации:**\n"
        "• Создавай больше желаний для увеличения активности\n"
        "• Будь активным в просмотре и оценке\n"
        "• Помогай другим находить единомышленников"
    )
    
    await message.answer(
        stats_text,
        reply_markup=MENU_KEYBOARD,
        parse_mode="MARKDOWN"
    )

# Обработчики для конкретных категорий - заменяем на один общий
@achievements_router.message(F.text.in_([
    "🎭 Развлечения", "⚽ Спорт и активность", "🍽️ Кулинария и еда", "✈️ Путешествия",
    "📚 Обучение и развитие", "👥 Общение и знакомства", "🎨 Творчество и искусство", "🧘 Здоровье и благополучие",
    "💼 Бизнес и карьера", "🏔️ Приключения и экстрим",
    # Добавляем старые сокращенные названия для обратной совместимости
    "⚽ Спорт", "🍽️ Кулинария", "📚 Обучение", "👥 Общение", "🎨 Творчество", "🧘 Здоровье", "💼 Бизнес", "🏔️ Приключения"
]))
async def category_button_handler(message: types.Message):
    """Handle all category button presses."""
    # Извлекаем название категории из текста кнопки
    category_name = message.text
    
    # Находим категорию по названию (убираем эмодзи)
    clean_name = category_name.split(' ', 1)[1] if ' ' in category_name else category_name
    
    categories = category_system.get_all_categories()
    category = None
    
    # Ищем категорию по частичному совпадению
    for cat in categories:
        if (clean_name.lower() in cat.name.lower() or 
            cat.name.lower().startswith(clean_name.lower())):
            category = cat
            break
    
    if category:
        await _show_category_details(message, category)
    else:
        # Показываем доступные категории для отладки
        available_categories = [f"• {cat.name}" for cat in categories]
        debug_text = (
            f"Категория '{clean_name}' не найдена.\n\n"
            "**Доступные категории:**\n" + "\n".join(available_categories) + "\n\n"
            "Попробуйте выбрать из списка категорий."
        )
        await message.answer(
            debug_text,
            reply_markup=MENU_KEYBOARD
        )


async def _show_category_details(message: types.Message, category):
    """Show detailed information about a category."""
    if not category:
        await message.answer("Категория не найдена")
        return
    
    # Получаем примеры желаний для категории
    examples = category_system.get_random_examples(category.id, 3)
    
    category_text = (
        f"{category.emoji} **{category.name}** {category.emoji}\n\n"
        f"**📝 Описание:**\n{category.description}\n\n"
        "**💭 Примеры желаний:**\n"
    )
    
    for example in examples:
        category_text += f"• {example}\n"
    
    category_text += f"\n**🔍 Хочешь посмотреть желания в этой категории?**\n"
    category_text += "Используй кнопки ниже для навигации!"
    
    # Создаем специальную клавиатуру для категорий
    from src.bot.structures.keyboards.dreams import CATEGORIES_MARKUP
    
    await message.answer(
        category_text,
        reply_markup=CATEGORIES_MARKUP,
        parse_mode="MARKDOWN"
    )

# Callback обработчики для inline кнопок
@achievements_router.callback_query(lambda c: c.data == "show_achievements")
async def show_achievements_callback(callback_query: types.CallbackQuery, db):
    """Show achievements via callback."""
    await callback_query.answer()
    
    # Создаем mock message объект с правильным user_id
    mock_message = type('MockMessage', (), {
        'from_user': type('MockUser', (), {
            'id': callback_query.from_user.id,
            'username': callback_query.from_user.username,
            'first_name': callback_query.from_user.first_name
        })(),
        'answer': callback_query.message.answer
    })()
    
    await achievements_handler(mock_message, db)


@achievements_router.callback_query(lambda c: c.data == "show_categories")
async def show_categories_callback(callback_query: types.CallbackQuery):
    """Show categories via callback."""
    await callback_query.answer()
    await categories_handler(callback_query.message)


@achievements_router.callback_query(lambda c: c.data == "show_stats")
async def show_stats_callback(callback_query: types.CallbackQuery, db):
    """Show stats via callback."""
    await callback_query.answer()
    
    # Создаем mock message объект с правильным user_id
    mock_message = type('MockMessage', (), {
        'from_user': type('MockUser', (), {
            'id': callback_query.from_user.id,
            'username': callback_query.from_user.username,
            'first_name': callback_query.from_user.first_name
        })(),
        'answer': callback_query.message.answer
    })()
    
    await stats_handler(mock_message, db)


@achievements_router.callback_query(lambda c: c.data == "show_help")
async def show_help_callback(callback_query: types.CallbackQuery):
    """Show help via callback."""
    await callback_query.answer()
    # Импортируем help_handler из help.py
    from src.bot.logic.help import help_handler
    await help_handler(callback_query.message)


# Новые обработчики для быстрого доступа
@achievements_router.callback_query(lambda c: c.data == "create_dream")
async def create_dream_callback(callback_query: types.CallbackQuery):
    """Create dream via callback."""
    await callback_query.answer("Создание желания")
    await callback_query.message.answer(
        "💭 **Создание нового желания** 💭\n\n"
        "Напиши название своего желания:",
        reply_markup=MENU_KEYBOARD,
        parse_mode="MARKDOWN"
    )


@achievements_router.callback_query(lambda c: c.data == "find_dreams")
async def find_dreams_callback(callback_query: types.CallbackQuery):
    """Find dreams via callback."""
    await callback_query.answer("Поиск желаний")
    await callback_query.message.answer(
        "🔍 **Поиск желаний** 🔍\n\n"
        "Нажми кнопку 'Желания' в главном меню для просмотра всех желаний!",
        reply_markup=MENU_KEYBOARD,
        parse_mode="MARKDOWN"
    )


@achievements_router.callback_query(lambda c: c.data == "show_profile")
async def show_profile_callback(callback_query: types.CallbackQuery, db):
    """Show profile via callback."""
    await callback_query.answer("Профиль")
    
    # Создаем mock message объект с правильным user_id
    mock_message = type('MockMessage', (), {
        'from_user': type('MockUser', (), {
            'id': callback_query.from_user.id,
            'username': callback_query.from_user.username,
            'first_name': callback_query.from_user.first_name
        })(),
        'answer': callback_query.message.answer
    })()
    
    from src.bot.logic.profile.select import profile_handler
    await profile_handler(mock_message, db)


@achievements_router.callback_query(lambda c: c.data == "show_my_dreams")
async def show_my_dreams_callback(callback_query: types.CallbackQuery, db):
    """Show my dreams via callback."""
    await callback_query.answer("Мои желания")
    
    # Создаем mock message объект с правильным user_id
    mock_message = type('MockMessage', (), {
        'from_user': type('MockUser', (), {
            'id': callback_query.from_user.id,
            'username': callback_query.from_user.username,
            'first_name': callback_query.from_user.first_name
        })(),
        'answer': callback_query.message.answer
    })()
    
    from src.bot.logic.profile.select import mydream_handler
    await mydream_handler(mock_message, db)
