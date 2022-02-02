from datetime import datetime
from typing import List, Optional

import pytz
from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup

from repository import Repository
from keyboards import get_start_menu_kb, get_claim_tmps_list_kb, get_claim_parts_kb, emojis


async def start_menu(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()
    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    await message.reply("Добрый день! Выберите одну из следующих команд:", reply_markup=start_menu_kb)


async def show_bot_info(message: types.Message):
    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    bot_info: str = """
Это бот, который поможет вам составить исковое заявление в суд по нарушениям трудового законодательства.

Мы должны предупредить вас об обработке персональных данных, в соответствии с ФЗ "О персональных данных". Если вы согласны, просто продолжайте работу с ботом в основном меню.

Зачем бот собирает данные: 
1. Чтобы заполнить ваши данные в исковом заявлении: фамилию, имя, отчество и адрес. Если вы не хотите указывать свои данные, можете указать любые, и потом исправить в итоговом файле вручную. 
2. Чтобы автоматически подобрать суд по вашему адресу. Если не хотите указывать свой адрес, вы можете указать любой и затем найти суд самостоятельно. 

Как бот хранит и уничтожает данные: ваши персональные данные будут храниться в зашифрованном виде в базе данных бота во время сессии заполнения заявления. 
Как только вы нажмёте кнопку "получить" - данные стираются полностью. Если вы выйдите из сессии, и при этом не нажмете кнопку "получить", данные также сотрутся автоматически через два часа.
    """
    await message.reply(bot_info, reply_markup=start_menu_kb)


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
    dp.register_message_handler(start_menu, commands=["start"], state="*")
    dp.register_message_handler(start_menu, filters.Regexp(f"^{emojis.left_arrow} назад"))
    dp.register_message_handler(show_bot_info, filters.Regexp(f"^{emojis.bookmark_tabs} узнать о боте$"))
    dp.register_message_handler(choose_claim_tmp, filters.Regexp(f"^{emojis.fist} выбор операции"))
    dp.register_message_handler(choose_claim_tmp, filters.Regexp(f"^{emojis.left_arrow} к шаблонам"))

    repository: Repository = Repository()
    tmp_names: List[str] = repository.get_tmps_list()
    tmp_regex: str = f"^{emojis.page_facing_up} ({'|'.join([tn for tn in tmp_names])})$"
    dp.register_message_handler(choose_claim_part, filters.Regexp(tmp_regex))
