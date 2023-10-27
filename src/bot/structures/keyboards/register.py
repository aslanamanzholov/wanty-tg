from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

REGISTER_START_CONFIRM = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="OK, давай начнем")]
    ],
    resize_keyboard=True
)

REGISTER_USER_GENDER = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мужчина"), KeyboardButton(text="Женщина")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

REGISTER_USER_COUNTRY = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Алматы"), KeyboardButton(text="Астана")],
        [KeyboardButton(text="Атырау"), KeyboardButton(text="Шымкент")],
        [KeyboardButton(text="Другой")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

REGISTER_SUCCESS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Dreams"), KeyboardButton(text="My Profile")]
    ],
    resize_keyboard=True
)