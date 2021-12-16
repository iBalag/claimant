from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import repository
from keyboards import emojis


def get_start_menu_kb() -> ReplyKeyboardMarkup:
    info_btn = KeyboardButton(f"{emojis.bookmark_tabs} информация")
    choose_claim_tmp_btn = KeyboardButton(f"{emojis.fist} выбор операции")
    start_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    start_menu_kb.row(info_btn, choose_claim_tmp_btn)
    return start_menu_kb


def get_claim_tmps_list_kb() -> ReplyKeyboardMarkup:
    tmp_names = repository.get_tmps_list()
    choose_claim_tmp_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for tmp_name in tmp_names:
        choose_claim_tmp_kb.add(KeyboardButton(f"{emojis.page_facing_up} {tmp_name}"))
    choose_claim_tmp_kb.add(KeyboardButton(f"{emojis.left_arrow} назад"))
    return choose_claim_tmp_kb
