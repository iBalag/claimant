from typing import List

from aiogram import types, Dispatcher, filters
from aiogram.types import ReplyKeyboardMarkup

import repository
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
    claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb()
    await message.reply("Выберите часть искового заявления для заполнения", reply_markup=claim_parts_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_menu, commands=["start", "назад"])
    dp.register_message_handler(show_bot_info, commands=["информация"])
    # dp.register_message_handler(choose_claim_tmp, filters.Regexp("^/выбор операции$"))
    dp.register_message_handler(choose_claim_tmp, filters.Regexp(f"^{emojis.fist} выбор операции"))

    tmp_names: List[str] = repository.get_tmps_list()
    tmp_regex: str = f"^/({'|'.join([tn for tn in tmp_names])})$"
    dp.register_message_handler(choose_claim_part, filters.Regexp(tmp_regex))

