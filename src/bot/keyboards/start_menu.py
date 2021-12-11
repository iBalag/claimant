from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import repository
from keyboards import emojis


def get_start_menu_kb() -> ReplyKeyboardMarkup:
    star_btn = KeyboardButton("/начать")
    info_btn = KeyboardButton("/информация")
    choose_claim_tmp_btn = KeyboardButton(f"{emojis.fist} выбор операции")
    start_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    start_menu_kb\
        .add(star_btn)\
        .add(info_btn)\
        .add(choose_claim_tmp_btn)
    return start_menu_kb


def get_claim_tmps_list_kb() -> ReplyKeyboardMarkup:
    tmp_names = repository.get_tmps_list()
    choose_claim_tmp_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for tmp_name in tmp_names:
        choose_claim_tmp_kb.add(KeyboardButton(f"/{tmp_name}"))
    choose_claim_tmp_kb.add(KeyboardButton("/назад"))
    return choose_claim_tmp_kb
