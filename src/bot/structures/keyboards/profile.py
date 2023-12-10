import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

PROFILE_MAIN_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желания {emoji.emojize(':thought_balloon:')}")],
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

channel_url = "https://t.me/projectology_101/"

INLINE_BUTTON_TG_CHANNEL_URL_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=f'{emoji.emojize(":newspaper:")} Проектология 101 {emoji.emojize(":newspaper:")}',
                              url=channel_url)]
    ]
)
