from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

DREAMS_MAIN_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Like"), KeyboardButton(text="Dislike"), KeyboardButton(text="Sleep")],
        [KeyboardButton(text="Write to a Dreamer")]
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