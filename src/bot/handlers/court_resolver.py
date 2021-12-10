from typing import List, Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

import repository
from keyboards import get_regions_list_kb

from common import CourtInfo, resolve_court_address


class ResolveCourt(StatesGroup):
    waiting_for_user_region = State()
    waiting_for_user_city = State()
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
    await message.answer("Введите название города, в котором вы прописаны с помощью команды /город. "
                         "Например: /город Москва", reply_markup=ReplyKeyboardRemove())


async def city_chosen(message: types.Message, state: FSMContext):
    city: Optional[str] = message.get_args()
    if city is None:
        # TODO: return keyboard with one button 'back to region choose'
        await message.answer("Введите название города, в котором вы прописаны с помощью команды /город. "
                             "Например: /город Москва", reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(chosen_city=city)
    await ResolveCourt.next()
    # TODO: return keyboard with one button 'back to region choose'
    await message.answer("Введите название улицы, на которой вы прописаны с помощью команды /улица. "
                         "Например: /улица Ленина", reply_markup=ReplyKeyboardRemove())


async def street_chosen(message: types.Message, state: FSMContext):
    street: Optional[str] = message.get_args()
    if street is None:
        # TODO: return keyboard with one button 'back to region choose'
        await message.answer("Введите название улицы, на которой вы прописаны с помощью команды /улица. "
                             "Например: /улица Ленина", reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(chosen_street=street)
    await ResolveCourt.next()

    user_data = await state.get_data()
    region_code: str = repository.get_region_code(user_data["chosen_region_name"])
    court_info: List[CourtInfo] = await resolve_court_address(city=user_data["chosen_city"],
                                                              court_subj=region_code, street=street)

    court_info_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    for court in court_info:
        court_btn: KeyboardButton = KeyboardButton(f"/суд {court.name} {court.address}")
        court_info_kb.add(court_btn)

    await message.reply("Выберите подходящий суд для подачи заявления:", reply_markup=court_info_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(header_start, filters.Regexp("^/шапка$"))
    dp.register_message_handler(region_chosen, filters.Regexp("^/регион"), state=ResolveCourt.waiting_for_user_region)
    dp.register_message_handler(city_chosen, filters.Regexp("^/город"), state=ResolveCourt.waiting_for_user_city)
    dp.register_message_handler(street_chosen, filters.Regexp("^/улица"), state=ResolveCourt.waiting_for_user_street)
