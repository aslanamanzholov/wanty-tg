import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

PROFILE_MAIN_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желании {emoji.emojize(':thought_balloon:')}")],
        [KeyboardButton(text=f"Создать желание {emoji.emojize(':thought_balloon:')}")]
    ],
    resize_keyboard=True
)

INLINE_BUTTON_PROFILE_EDIT_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Изменить', callback_data='edit_dream')],
        [InlineKeyboardButton(text='Удалить', callback_data='delete_dream')]
    ]
)
