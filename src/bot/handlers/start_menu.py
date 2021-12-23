from datetime import datetime
from typing import List, Optional

import pytz
from aiogram import types, Dispatcher, filters
from aiogram.types import ReplyKeyboardMarkup

from repository import Repository
from keyboards import get_start_menu_kb, get_claim_tmps_list_kb, get_claim_parts_kb, emojis


async def start_menu(message: types.Message):
    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    await message.reply("Добрый день! Выберите одну из следующих команд:", reply_markup=start_menu_kb)


async def show_bot_info(message: types.Message):
    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    await message.reply("Тут будет полезная информация по боту", reply_markup=start_menu_kb)


async def choose_claim_tmp(message: types.Message):
    claim_tmps_list_kb: ReplyKeyboardMarkup = get_claim_tmps_list_kb()
    await message.reply("Выберите один из шаблонов для заполнения", reply_markup=claim_tmps_list_kb)


async def choose_claim_part(message: types.Message):
    # This is the first time when the user chose the claim template.
    temp_theme_raw: str = message.text
    temp_theme: str = temp_theme_raw.replace(emojis.page_facing_up, "").strip()
    repository: Repository = Repository()
    previous_claim_data: Optional[dict] = repository.get_claim_data(message.from_user.id, temp_theme)
    if previous_claim_data is not None:
        repository.remove_item("claim-data", previous_claim_data["_id"])

    new_claim_data: dict = {
        "user_id": message.from_user.id,
        "claim_theme": temp_theme,
        "created": datetime.utcnow().replace(tzinfo=pytz.UTC)
    }
    repository.insert_item("claim-data", new_claim_data)
    claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb(message.from_user.id)
    await message.reply("Выберите часть искового заявления для заполнения", reply_markup=claim_parts_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_menu, commands=["start"])
    dp.register_message_handler(start_menu, filters.Regexp(f"^{emojis.left_arrow} назад"))
    dp.register_message_handler(show_bot_info, filters.Regexp(f"^{emojis.bookmark_tabs} информация$"))
    dp.register_message_handler(choose_claim_tmp, filters.Regexp(f"^{emojis.fist} выбор операции"))
    dp.register_message_handler(choose_claim_tmp, filters.Regexp(f"^{emojis.left_arrow} к выбору\nчасти заявления"))

    repository: Repository = Repository()
    tmp_names: List[str] = repository.get_tmps_list()
    tmp_regex: str = f"^{emojis.page_facing_up} ({'|'.join([tn for tn in tmp_names])})$"
    dp.register_message_handler(choose_claim_part, filters.Regexp(tmp_regex))

