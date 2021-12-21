from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_claim_parts_kb() -> ReplyKeyboardMarkup:
    # TODO: add OK emoji for filled parts
    claim_parts_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    claim_parts_kb\
        .add(KeyboardButton("/шапка")) \
        .add(KeyboardButton("/тема заявления")) \
        .add(KeyboardButton("/фабула")) \
        .add(KeyboardButton("/суть нарушения")) \
        .add(KeyboardButton("/доказательства")) \
        .add(KeyboardButton("/нормативное обоснование")) \
        .add(KeyboardButton("/требования")) \
        .add(KeyboardButton("/приложения")) \
        .add(KeyboardButton("/назад"))
    return claim_parts_kb
