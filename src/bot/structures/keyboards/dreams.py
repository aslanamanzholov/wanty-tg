import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Inline клавиатура для основных действий с желаниями
DREAMS_MAIN_INLINE_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❤️ Лайк", callback_data="like_dream"),
            InlineKeyboardButton(text="👎 Дизлайк", callback_data="dislike_dream")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
)

# Клавиатура для случаев, когда желания не найдены
DREAMS_NOT_FOUND_INLINE_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💭 Создать желание", callback_data="create_dream"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ],
        [
            InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="retry_dreams")
        ]
    ]
)

# Клавиатура для регистрации
REGISTRATION_REQUIRED_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Начать регистрацию", callback_data="start_registration"),
            InlineKeyboardButton(text="❓ Как это работает?", callback_data="how_it_works")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
)

# Клавиатура для выбора категории при создании желания
CATEGORY_SELECTION_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🏔️ Приключения и экстрим", callback_data="cat_adventure"),
            InlineKeyboardButton(text="🎨 Творчество и искусство", callback_data="cat_creativity")
        ],
        [
            InlineKeyboardButton(text="💻 Технологии и наука", callback_data="cat_technology"),
            InlineKeyboardButton(text="🏃 Спорт и здоровье", callback_data="cat_sports")
        ],
        [
            InlineKeyboardButton(text="🌍 Путешествия", callback_data="cat_travel"),
            InlineKeyboardButton(text="📚 Образование", callback_data="cat_education")
        ],
        [
            InlineKeyboardButton(text="🎭 Развлечения", callback_data="cat_entertainment"),
            InlineKeyboardButton(text="🤝 Социальные проекты", callback_data="cat_social")
        ]
    ]
)

# Клавиатура для навигации по категориям
CATEGORIES_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🏔️ Приключения и экстрим", callback_data="cat_adventure"),
            InlineKeyboardButton(text="🎨 Творчество и искусство", callback_data="cat_creativity")
        ],
        [
            InlineKeyboardButton(text="💻 Технологии и наука", callback_data="cat_technology"),
            InlineKeyboardButton(text="🏃 Спорт и здоровье", callback_data="cat_sports")
        ],
        [
            InlineKeyboardButton(text="🌍 Путешествия", callback_data="cat_travel"),
            InlineKeyboardButton(text="📚 Образование", callback_data="cat_education")
        ],
        [
            InlineKeyboardButton(text="🎭 Развлечения", callback_data="cat_entertainment"),
            InlineKeyboardButton(text="🤝 Социальные проекты", callback_data="cat_social")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к желаниям", callback_data="back_to_dreams")
        ]
    ]
)

# Простая кнопка отмены
CANCEL_BUTTON = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)