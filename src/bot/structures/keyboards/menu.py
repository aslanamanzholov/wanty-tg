import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MENU_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=f"Желании {emoji.emojize(':thought_balloon:')}"),
            KeyboardButton(text='Мои желания'), KeyboardButton(text=f'Изменить имя {emoji.emojize(":writing_hand:")}')
        ],
    ],
    resize_keyboard=True
)
