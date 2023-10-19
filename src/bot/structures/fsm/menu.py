from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MENU_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мои желании'), KeyboardButton(text='Мои профиль')],
    ],
    resize_keyboard=True
)