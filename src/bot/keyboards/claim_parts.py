from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from keyboards import emojis


def get_claim_parts_kb() -> ReplyKeyboardMarkup:
    # TODO: add OK emoji for filled parts
    claim_parts_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    claim_parts_kb\
        .add(KeyboardButton(f"{emojis.top_hat} шапка")) \
        .add(KeyboardButton(f"{emojis.speech_balloon} фабула")) \
        .add(KeyboardButton("/суть нарушения")) \
        .add(KeyboardButton("/доказательства")) \
        .add(KeyboardButton("/нормативное обоснование")) \
        .add(KeyboardButton("/требования")) \
        .add(KeyboardButton("/приложения")) \
        .add(KeyboardButton("/назад"))
    return claim_parts_kb
