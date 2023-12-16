import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

DREAMS_MAIN_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=emoji.emojize(":red_heart:")),
         KeyboardButton(text=emoji.emojize(":thumbs_down:")), KeyboardButton(text=emoji.emojize(":ZZZ:"))],
        [KeyboardButton(text=f"Создать желание {emoji.emojize(':thought_balloon:')}")]
    ],
    resize_keyboard=True
)

DREAMS_CALLBACK_FROM_USER_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text=emoji.emojize(":thumbs_down:"))]
    ],
    resize_keyboard=True
)

DREAMS_NOT_FOUND_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желания {emoji.emojize(':thought_balloon:')}"), KeyboardButton(text="Создать желание"),
         KeyboardButton(text=emoji.emojize(":ZZZ:"))],
        [KeyboardButton(text="Мои желания")]
    ],
    resize_keyboard=True
)

DREAMS_NOT_FOUND_BUTTONS_PROFILE_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желания {emoji.emojize(':thought_balloon:')}"), KeyboardButton(text="Создать желание"),
         KeyboardButton(text=emoji.emojize(":ZZZ:"))]
    ],
    resize_keyboard=True
)

CANCEL_BUTTON = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

CANCEL_WITHOUT_IMAGE_BUTTON = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Без изображений"), KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

CANCEL_WITHOUT_DETAILS_BUTTON = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Без подробностей"), KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

LIKE_DISLIKE_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желания {emoji.emojize(':thought_balloon:')}"), KeyboardButton(text=emoji.emojize(":ZZZ:"))]
    ],
    resize_keyboard=True
)

SLEEP_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Желания {emoji.emojize(':thought_balloon:')}"), KeyboardButton(text="Мои желания")]
    ],
    resize_keyboard=True
)