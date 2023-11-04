import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

DREAMS_MAIN_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Создать желание {emoji.emojize(':thought_balloon:')}")],
        [KeyboardButton(text=emoji.emojize(":red_heart:")),
         KeyboardButton(text=emoji.emojize(":thumbs_down:")), KeyboardButton(text=emoji.emojize(":ZZZ:"))],
        [KeyboardButton(text=emoji.emojize(":love_letter:"))]
    ],
    resize_keyboard=True
)

DREAMS_NOT_FOUND_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желании {emoji.emojize(':thought_balloon:')}"), KeyboardButton(text="Создать желание"),
         KeyboardButton(text=emoji.emojize(":ZZZ:"))],
        [KeyboardButton(text="Мои желании")]
    ],
    resize_keyboard=True
)

DREAMS_NOT_FOUND_BUTTONS_PROFILE_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желании {emoji.emojize(':thought_balloon:')}"), KeyboardButton(text="Создать желанию"),
         KeyboardButton(text=emoji.emojize(":ZZZ:"))]
    ],
    resize_keyboard=True
)

LIKE_DISLIKE_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желании {emoji.emojize(':thought_balloon:')}"), KeyboardButton(text=emoji.emojize(":ZZZ:"))]
    ],
    resize_keyboard=True
)

SLEEP_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желании {emoji.emojize(':thought_balloon:')}"), KeyboardButton(text="Мои желании")]
    ],
    resize_keyboard=True
)