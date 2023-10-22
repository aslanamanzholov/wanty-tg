from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

DREAMS_MAIN_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Create")],
        [KeyboardButton(text="Like"), KeyboardButton(text="Dislike"), KeyboardButton(text="Sleep")],
        [KeyboardButton(text="Write to")]
    ],
    resize_keyboard=True
)

DREAMS_NOT_FOUND_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Dreams"), KeyboardButton(text="Create Dream"), KeyboardButton(text="Sleep")],
        [KeyboardButton(text="My profile")]
    ],
    resize_keyboard=True
)

LIKE_DISLIKE_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Dreams"), KeyboardButton(text="Sleep")]
    ],
    resize_keyboard=True
)

SLEEP_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Dreams"), KeyboardButton(text="My profile")]
    ],
    resize_keyboard=True
)