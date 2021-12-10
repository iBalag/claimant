from typing import List

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class ResolveCourt(StatesGroup):
    waiting_for_court_region = State()
    waiting_for_user_street = State()
    waiting_for_court_chosen = State()


async def input_court_region(message: types.Message, state: FSMContext):
    await message.reply("Выберите варианты:", reply_markup=start_menu_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(input_court_region, filters.Regexp("^/выберите регион$"))