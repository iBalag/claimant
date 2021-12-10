from typing import List, Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

import repository
from keyboards import get_regions_list_kb


class ResolveCourt(StatesGroup):
    waiting_for_user_region = State()
    waiting_for_user_street = State()
    waiting_for_court_chosen = State()


async def header_start(message: types.Message):
    regions_list_kb: ReplyKeyboardMarkup = get_regions_list_kb()
    await message.reply("Выберите свой регион:", reply_markup=regions_list_kb)
    await ResolveCourt.waiting_for_user_region.set()


async def region_chosen(message: types.Message, state: FSMContext):
    region_name: Optional[str] = message.get_args()
    available_region_names: List[str] = [region["name"] for region in repository.get_regions_list()]
    if region_name is None or region_name not in available_region_names:
        await message.answer("Пожалуйста, выберите регион, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_region_name=region_name)
    await ResolveCourt.next()
    # TODO: return keyboard with one button 'back to region choose'
    await message.answer("Введите название улицы, на которой вы прописаны с помощью команды /улица. "
                         "Например /улица Ленина", reply_markup=ReplyKeyboardRemove())


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(header_start, filters.Regexp("^/шапка$"))
    dp.register_message_handler(region_chosen, filters.Regexp("^/регион"), state=ResolveCourt.waiting_for_user_region)
