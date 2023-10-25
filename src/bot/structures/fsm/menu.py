from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MENU_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Dreams'), KeyboardButton(text='My Profile')],
    ],
    resize_keyboard=True
)