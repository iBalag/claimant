from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from keyboards import emojis

example_btn = KeyboardButton(f"{emojis.red_question_mark} показать пример")


def get_common_start_kb() -> ReplyKeyboardMarkup:
    chose_option_btn = KeyboardButton(f"{emojis.card_file_box} выбрать из списка")
    common_start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    common_start_kb.row(example_btn, chose_option_btn)
    return common_start_kb


def get_next_actions_kb() -> ReplyKeyboardMarkup:
    another_option_btn: KeyboardButton = KeyboardButton(f"{emojis.card_file_box} добавить еще из списка")
    compose_btn: KeyboardButton = KeyboardButton(f"{emojis.chequered_flag} закончить заполнение")
    next_actions_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    next_actions_kb.add(example_btn) \
        .add(another_option_btn) \
        .add(compose_btn)
    return next_actions_kb
