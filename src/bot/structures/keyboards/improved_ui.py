"""Improved UI components for better user experience."""
import emoji
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton
)

# 🎯 Основные действия
MAIN_ACTIONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=f"🔍 Найти желания"),
            KeyboardButton(text=f"✨ Создать желание")
        ],
        [
            KeyboardButton(text=f"👤 Мой профиль"),
            KeyboardButton(text=f"📊 Статистика")
        ],
        [
            KeyboardButton(text=f"💡 Как это работает"),
            KeyboardButton(text=f"🎁 Бонусы")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие..."
)

# 🎮 Игровые кнопки для желаний
DREAM_ACTIONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=f"💖 Нравится!"),
            KeyboardButton(text=f"💔 Не подходит"),
            KeyboardButton(text=f"⏭️ Следующее")
        ],
        [
            KeyboardButton(text=f"💬 Комментарий"),
            KeyboardButton(text=f"🔖 Сохранить")
        ],
        [
            KeyboardButton(text=f"🏠 Главное меню")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Что думаешь об этом желании?"
)

# 🎨 Создание желания
CREATE_DREAM_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=f"📝 Текст"),
            KeyboardButton(text=f"🖼️ Фото")
        ],
        [
            KeyboardButton(text=f"📍 Место"),
            KeyboardButton(text=f"⏰ Время")
        ],
        [
            KeyboardButton(text=f"🔙 Назад"),
            KeyboardButton(text=f"✅ Готово")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Опиши свое желание..."
)

# 🎯 Профиль пользователя
PROFILE_ACTIONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=f"✏️ Редактировать"),
            KeyboardButton(text=f"🎨 Аватар")
        ],
        [
            KeyboardButton(text=f"🔒 Приватность"),
            KeyboardButton(text=f"📱 Уведомления")
        ],
        [
            KeyboardButton(text=f"🏠 Главное меню")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Управление профилем..."
)

# 🎁 Бонусы и достижения
BONUSES_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=f"🏆 Достижения"),
            KeyboardButton(text=f"🎯 Цели")
        ],
        [
            KeyboardButton(text=f"💎 Бонусы"),
            KeyboardButton(text=f"📈 Рейтинг")
        ],
        [
            KeyboardButton(text=f"🏠 Главное меню")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите раздел..."
)

# 🎮 Inline кнопки для интерактивности
QUICK_ACTIONS_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Быстрый старт", callback_data="quick_start"),
            InlineKeyboardButton(text="🎯 Цель дня", callback_data="daily_goal")
        ],
        [
            InlineKeyboardButton(text="💡 Случайное желание", callback_data="random_dream"),
            InlineKeyboardButton(text="🌟 Топ недели", callback_data="weekly_top")
        ],
        [
            InlineKeyboardButton(text="📱 Поделиться", switch_inline_query="Хочешь найти единомышленников?")
        ]
    ]
)

# 🎨 Категории желаний
DREAM_CATEGORIES_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🎭 Развлечения", callback_data="cat_entertainment"),
            InlineKeyboardButton(text="🏃‍♂️ Спорт", callback_data="cat_sport")
        ],
        [
            InlineKeyboardButton(text="🍽️ Еда", callback_data="cat_food"),
            InlineKeyboardButton(text="✈️ Путешествия", callback_data="cat_travel")
        ],
        [
            InlineKeyboardButton(text="📚 Обучение", callback_data="cat_learning"),
            InlineKeyboardButton(text="🎨 Творчество", callback_data="cat_creativity")
        ],
        [
            InlineKeyboardButton(text="🔍 Все категории", callback_data="cat_all")
        ]
    ]
)

# 🎯 Фильтры поиска
SEARCH_FILTERS_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Возраст", callback_data="filter_age"),
            InlineKeyboardButton(text="📍 Место", callback_data="filter_location")
        ],
        [
            InlineKeyboardButton(text="🎯 Категория", callback_data="filter_category"),
            InlineKeyboardButton(text="⏰ Время", callback_data="filter_time")
        ],
        [
            InlineKeyboardButton(text="🔍 Применить фильтры", callback_data="apply_filters")
        ]
    ]
)

# 🎁 Система достижений
ACHIEVEMENTS_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🥇 Первый шаг", callback_data="achievement_first"),
            InlineKeyboardButton(text="💝 Сердцеед", callback_data="achievement_hearts")
        ],
        [
            InlineKeyboardButton(text="🌟 Популярность", callback_data="achievement_popular"),
            InlineKeyboardButton(text="🎯 Целеустремленность", callback_data="achievement_goals")
        ],
        [
            InlineKeyboardButton(text="📊 Все достижения", callback_data="achievements_all")
        ]
    ]
)
