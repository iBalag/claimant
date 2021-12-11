from typing import List, Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import aiogram.utils.markdown as fmt

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
    if len(court_info) == 0:
        await ResolveCourt.waiting_for_user_city.set()
        await message.reply(f"Для данного города '{user_data['chosen_сity']}' и улицы '{user_data['chosen_street']}' "
                            f"не найдено суда. Пожалуйста, попробуйте ввести другой город или улицу.",
                            reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(court_info=court_info)
    for i, c_info in enumerate(court_info, 1):
        await message.reply(fmt.text(
            fmt.text(fmt.hunderline(f"{i}. Название:"), f" {c_info.name}"),
            fmt.text(f"Адрес: {c_info.address}",),
            fmt.text(f"Примечание: {c_info.note}"),
            sep="\n"
        ), parse_mode="HTML")

    await ResolveCourt.waiting_for_court_chosen.set()
    await message.reply("Выберите подходящий суд для подачи заявления с помощью команды /суд. "
                        "Например: /суд 1", reply_markup=ReplyKeyboardRemove())


async def court_chosen(message: types.Message, state: FSMContext):
    court_number_raw: Optional[str] = message.get_args()
    if court_number_raw is None or court_number_raw.isdigit():
        # TODO: return keyboard with one button 'back to region choose'
        await message.reply("Выберите подходящий суд для подачи заявления с помощью команды /суд. "
                            "Например: /суд 1", reply_markup=ReplyKeyboardRemove())
        return

    user_data = await state.get_data()
    chosen_court: CourtInfo = user_data['court_info'][int(court_number_raw) - 1]
    await message.reply(fmt.text(
        fmt.text("Выбранный суд:", ),
        fmt.text(fmt.hunderline(f"Название:"), f" {chosen_court.name}"),
        fmt.text(f"Адрес: {chosen_court.address}", ),
        sep="\n"
    ), parse_mode="HTML")

    # TODO: Save to DB
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(header_start, filters.Regexp("^/шапка$"))
    dp.register_message_handler(region_chosen, filters.Regexp("^/регион"), state=ResolveCourt.waiting_for_user_region)
    dp.register_message_handler(city_chosen, filters.Regexp("^/город"), state=ResolveCourt.waiting_for_user_city)
    dp.register_message_handler(street_chosen, filters.Regexp("^/улица"), state=ResolveCourt.waiting_for_user_street)
    dp.register_message_handler(court_chosen, filters.Regexp("^/суд"), state=ResolveCourt.waiting_for_court_chosen)
