from aiogram import types, Dispatcher
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


star_btn = KeyboardButton("Начать")
info_btn = KeyboardButton("Информация")
start_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_menu_kb.add(star_btn).add(info_btn)


async def start_menu(message: types.Message):
    await message.reply("Выберите варианты:", reply_markup=start_menu_kb)


async def show_bot_info(message: types.Message):
    await message.reply("Тут будет полная информация по боту", reply_markup=start_menu_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_bot_info, commands=["Информация"])
    dp.register_message_handler(callback=start_menu)
