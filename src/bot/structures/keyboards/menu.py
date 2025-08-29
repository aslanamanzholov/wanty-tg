import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

MENU_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=f"Желания {emoji.emojize(':thought_balloon:')}"),
            KeyboardButton(text='Мои желания')
        ],
        [
            KeyboardButton(text=f'Создать желание {emoji.emojize(":sparkles:")}'),
            KeyboardButton(text=f'Изменить имя {emoji.emojize(":writing_hand:")}')
        ],
        [
            KeyboardButton(text='👤 Профиль')
        ]
    ],
    resize_keyboard=True
)

# Inline клавиатура для дополнительных функций
ADDITIONAL_FEATURES_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💭 Создать желание", callback_data="create_dream"),
            InlineKeyboardButton(text="🏆 Достижения", callback_data="show_achievements")
        ],
        [
            InlineKeyboardButton(text="📂 Категории", callback_data="show_categories"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats")
        ],
        [
            InlineKeyboardButton(text="❓ Справка", callback_data="show_help")
        ]
    ]
)

# Клавиатура для быстрого доступа к основным функциям
QUICK_ACCESS_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💭 Создать желание", callback_data="create_dream"),
            InlineKeyboardButton(text="🔍 Найти желания", callback_data="find_dreams")
        ],
        [
            InlineKeyboardButton(text="👤 Мой профиль", callback_data="show_profile"),
            InlineKeyboardButton(text="⭐ Мои желания", callback_data="show_my_dreams")
        ]
    ]
)
