import re
from typing import List, Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import aiogram.utils.markdown as fmt

import repository

from common import CourtInfo, resolve_court_address


class ResolveCourt(StatesGroup):
    waiting_for_user_post_code = State()
    waiting_for_user_city = State()
    waiting_for_user_street = State()
    waiting_for_user_house = State()
    waiting_for_user_apartment = State()
    waiting_for_court_chosen = State()
    waiting_for_employer_name = State()
    waiting_for_employer_address = State()


async def header_start(message: types.Message):
    await message.reply("Для заполнения шапки заявления необходимо указать:\n"
                        "- Наименование и адрес суда\n"
                        "- ФИО и адрес истца\n"
                        "- Наименование и адрес ответчика\n")
    await message.answer("Внимание! Поиск подходящего суда будет происходить по адресу истца.")
    await message.answer("Введите свой почтовый индекс", reply_markup=ReplyKeyboardRemove())
    await ResolveCourt.waiting_for_user_post_code.set()


async def post_code_chosen(message: types.Message, state: FSMContext):
    user_post_code: Optional[str] = message.text
    # TODO: add checking by real post code
    if re.match("\\d{6}", user_post_code) is None:
        await message.reply("Неверный индекс. Введите свой почтовый индекс", reply_markup=ReplyKeyboardRemove())
    await state.update_data(user_post_code=user_post_code)
    await ResolveCourt.waiting_for_user_city.set()
    await message.reply("Спасибо, а теперь укажите свой город", reply_markup=ReplyKeyboardRemove())


async def city_chosen(message: types.Message, state: FSMContext):
    city: Optional[str] = message.text
    # TODO: Add checking for city value
    await state.update_data(chosen_city=city)
    await ResolveCourt.waiting_for_user_street.set()
    # TODO: return keyboard with one button 'back'
    await message.reply("Принято товарищ! А теперь укажите название улицы, на которой вы прописаны",
                        reply_markup=ReplyKeyboardRemove())


async def street_chosen(message: types.Message, state: FSMContext):
    street: Optional[str] = message.text
    await state.update_data(chosen_street=street)
    await ResolveCourt.waiting_for_user_house.set()
    await message.reply("Принято товарищ! А теперь введи номер своего дома",
                        reply_markup=ReplyKeyboardRemove())


async def house_chosen(message: types.Message, state: FSMContext):
    house: Optional[str] = message.text
    await state.update_data(house_chosen=house)
    await ResolveCourt.waiting_for_user_apartment.set()
    await message.reply("Принято товарищ! А теперь введи номер своей квартиры. "
                        "Если ты живешь в частном доме, просто ответь: нет",
                        reply_markup=ReplyKeyboardRemove())


async def apartment_chosen(message: types.Message, state: FSMContext):
    apartment: Optional[str] = message.text
    if apartment == "нет":
        await state.update_data(apartment_chosen="")
    elif not apartment.isdigit():
        await message.reply("Номер дома нужно указать цифрой. "
                            "Если ты живешь в частном доме, просто ответь: нет",
                            reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(apartment_chosen=apartment)
    user_data = await state.get_data()
    region_code: str = repository.get_region_code(user_data["user_post_code"])
    court_info: List[CourtInfo] = await resolve_court_address(city=user_data["chosen_city"],
                                                              court_subj=region_code, street=user_data["chosen_street"])
    if len(court_info) == 0:
        # TODO: provide user ability to enter court info by himself
        await ResolveCourt.waiting_for_user_city.set()
        await message.reply(f"Для данного города '{user_data['chosen_city']}' и улицы '{user_data['chosen_street']}' "
                            f"не найдено суда. Пожалуйста, попробуйте ввести другой город или улицу.",
                            reply_markup=ReplyKeyboardRemove())
        return

    if len(court_info) == 1:
        await state.update_data(chosen_court=court_info[0])
        await ResolveCourt.waiting_for_employer_name.set()
        await message.answer("Введите название организации, в которой вы работаете")
        return

    await state.update_data(court_info=court_info)
    for i, c_info in enumerate(court_info, 1):
        await message.reply(fmt.text(
            fmt.text(fmt.bold(f"{i}. {c_info.name}")),
            fmt.text(f"Адрес: {c_info.address}",),
            fmt.text(f"Примечание: {c_info.note}"),
            sep="\n"
        ), parse_mode="HTML")

    await ResolveCourt.waiting_for_court_chosen.set()
    court_options: List[str] = [str(i) for i in list(range(1, len(court_info) + 1))]
    await message.reply(f"Выберите подходящий суд для подачи заявления: "
                        f"{', '.join(court_options)}",
                        reply_markup=ReplyKeyboardRemove())


async def court_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    court_info: List[CourtInfo] = user_data['court_info']
    court_number_raw: Optional[str] = message.text
    if court_number_raw is None or not court_number_raw.isdigit() \
            or int(court_number_raw) not in list(range(len(court_info)+1)):
        court_options: List[str] = [str(i) for i in list(range(1, len(court_info) + 1))]
        await message.reply(f"Выберите подходящий суд для подачи заявления: {', '.join(court_options)}",
                            reply_markup=ReplyKeyboardRemove())
        return

    chosen_court: CourtInfo = user_data["court_info"][int(court_number_raw) - 1]
    await state.update_data(chosen_court=chosen_court)
    await ResolveCourt.waiting_for_employer_name.set()
    await message.answer("Введите название организации, в которой вы работаете. Например: OOO \"Рога и Копыта\"")


async def employer_name_chosen(message: types.Message, state: FSMContext):
    employer_name: Optional[str] = message.text
    await state.update_data(chosen_employer_name=employer_name)
    await ResolveCourt.waiting_for_employer_address.set()
    await message.reply("Принято товарищ! А теперь введи адрес организации, в которой вы работаете. "
                        "Например: 101002, ул. Любая, д.4",
                        reply_markup=ReplyKeyboardRemove())


async def employer_address_chosen(message: types.Message, state: FSMContext):
    employer_address: Optional[str] = message.text
    await state.update_data(chosen_employer_address=employer_address)
    user_data = await state.get_data()
    await message.answer(f"Проверьте введенные данные: {user_data}")
    # TODO: save to db
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(header_start, filters.Regexp("^/шапка$"))
    dp.register_message_handler(post_code_chosen, state=ResolveCourt.waiting_for_user_post_code)
    dp.register_message_handler(city_chosen, state=ResolveCourt.waiting_for_user_city)
    dp.register_message_handler(street_chosen, state=ResolveCourt.waiting_for_user_street)
    dp.register_message_handler(house_chosen, state=ResolveCourt.waiting_for_user_house)
    dp.register_message_handler(apartment_chosen, state=ResolveCourt.waiting_for_user_apartment)
    dp.register_message_handler(court_chosen, state=ResolveCourt.waiting_for_court_chosen)
    dp.register_message_handler(employer_name_chosen, state=ResolveCourt.waiting_for_employer_name)
    dp.register_message_handler(employer_address_chosen, state=ResolveCourt.waiting_for_employer_address)
