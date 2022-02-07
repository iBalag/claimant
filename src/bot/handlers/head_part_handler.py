import re
from typing import List, Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import aiogram.utils.markdown as fmt

from keyboards import emojis, get_claim_parts_kb
from repository import Repository

from common import CourtInfo, resolve_court_address


class HeadPart(StatesGroup):
    waiting_for_user_name = State()
    waiting_for_user_post_code = State()
    waiting_for_user_city = State()
    waiting_for_user_street = State()
    waiting_for_user_house = State()
    waiting_for_user_apartment = State()
    waiting_for_option_chosen = State()
    waiting_for_court_entered = State()
    waiting_for_court_chosen = State()
    waiting_for_employer_name = State()
    waiting_for_employer_address = State()


async def header_start(message: types.Message):
    await message.reply("Для заполнения шапки заявления необходимо указать:\n"
                        "- ФИО и адрес истца\n"
                        "- Наименование и адрес суда\n"
                        "- Наименование и адрес ответчика\n")
    await message.answer("Внимание! Поиск подходящего суда будет происходить по адресу истца.")
    await message.answer("Введите свои ФИО. Например: Иванов Сергей Владимирович", reply_markup=ReplyKeyboardRemove())
    await HeadPart.waiting_for_user_name.set()


async def user_name_chosen(message: types.Message, state: FSMContext):
    user_name: Optional[str] = message.text
    if len(user_name.split(" ")) != 3:
        await message.reply("ФИО введено неверно. Должно быть 3 слова. Попробуйте еще раз.",
                            reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(user_name=user_name)
    await HeadPart.waiting_for_user_post_code.set()
    await message.answer("Введите свой почтовый индекс", reply_markup=ReplyKeyboardRemove())


async def post_code_chosen(message: types.Message, state: FSMContext):
    user_post_code: Optional[str] = message.text
    # TODO: add checking by real post code
    if re.match("\\d{6}", user_post_code) is None:
        await message.reply("Неверный индекс. Введите свой почтовый индекс", reply_markup=ReplyKeyboardRemove())
    await state.update_data(user_post_code=user_post_code)
    await HeadPart.waiting_for_user_city.set()
    await message.reply("Спасибо, а теперь укажите свой город", reply_markup=ReplyKeyboardRemove())


async def city_chosen(message: types.Message, state: FSMContext):
    city: Optional[str] = message.text
    # TODO: Add checking for city value
    await state.update_data(chosen_city=city)
    await HeadPart.waiting_for_user_street.set()
    # TODO: return keyboard with one button 'back'
    await message.reply("Принято товарищ! А теперь укажите название улицы, на которой вы прописаны",
                        reply_markup=ReplyKeyboardRemove())


async def street_chosen(message: types.Message, state: FSMContext):
    street: Optional[str] = message.text
    await state.update_data(chosen_street=street)
    await HeadPart.waiting_for_user_house.set()
    await message.reply("Принято товарищ! А теперь введи номер своего дома",
                        reply_markup=ReplyKeyboardRemove())


async def house_chosen(message: types.Message, state: FSMContext):
    house: Optional[str] = message.text
    await state.update_data(house_chosen=house)
    await HeadPart.waiting_for_user_apartment.set()
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
    else:
        await state.update_data(apartment_chosen=apartment)
    user_data = await state.get_data()
    repository: Repository = Repository()
    region_code: str = repository.get_region_code(user_data["user_post_code"])
    court_info: List[CourtInfo] = await resolve_court_address(city=user_data["chosen_city"],
                                                              court_subj=region_code, street=user_data["chosen_street"])
    if len(court_info) == 0:
        chose_another_city_btn = KeyboardButton(f"{emojis.compass} выбрать другой город")
        enter_court_btn = KeyboardButton(f"{emojis.face_with_monocle} указать суд самостоятельно")
        options_kb = ReplyKeyboardMarkup(resize_keyboard=True)
        options_kb.row(chose_another_city_btn, enter_court_btn)
        await HeadPart.waiting_for_option_chosen.set()
        await message.reply(f"Для данного города '{user_data['chosen_city']}' и улицы '{user_data['chosen_street']}' "
                            f"не найдено суда. Пожалуйста, выберите одну из следующий опций:",
                            reply_markup=options_kb)
        return

    if len(court_info) == 1:
        await message.answer("По введенным данным найдет следующий суд:")
        await message.answer(fmt.text(
            fmt.text(f"{court_info[0].name}"),
            fmt.text(f"Адрес: {court_info[0].address}", ),
            fmt.text(f"Примечание: {court_info[0].note}"),
            sep="\n"
        ), parse_mode="HTML")
        await state.update_data(chosen_court=court_info[0])
        await HeadPart.waiting_for_employer_name.set()
        await message.answer("Введите название организации и её ИНН, в которой вы работаете. "
                             "Если не знаете ИНН, введите просто название.\n"
                             "Например: OOO \"Рога и Копыта\" (ИНН 555555555555)")
        return

    await state.update_data(court_info=court_info)
    for i, c_info in enumerate(court_info, 1):
        await message.answer(fmt.text(
            fmt.text(f"{i}. {c_info.name}"),
            fmt.text(f"Адрес: {c_info.address}",),
            fmt.text(f"Примечание: {c_info.note}"),
            sep="\n"
        ), parse_mode="HTML")

    await HeadPart.waiting_for_court_chosen.set()

    court_options_kb = InlineKeyboardMarkup()
    for i in range(len(court_info)):
        option_btn = InlineKeyboardButton(f"{i + 1}", callback_data=f"option {i}")
        court_options_kb.insert(option_btn)

    await message.answer(f"Выберите подходящий суд для подачи заявления:", reply_markup=court_options_kb)


async def option_chosen(message: types.Message, state: FSMContext):
    option: Optional[str] = message.text
    if option.endswith("выбрать другой город"):
        await HeadPart.waiting_for_user_city.set()
        await message.answer("Укажите свой город", reply_markup=ReplyKeyboardRemove())
        return
    if option.endswith("указать суд самостоятельно"):
        await HeadPart.waiting_for_court_entered.set()
        await message.answer("Укажите наименование и адрес суда. Например:\n"
                             "Фрунзенский районный суд г. Иваново, 153003, г. Иваново, ул. Мархлевского, д. 33",
                             reply_markup=ReplyKeyboardRemove())
        return


async def court_entered(message: types.Message, state: FSMContext):
    court_info_raw: Optional[str] = message.text
    court_info_agg: List[str] = re.split(",?\\s*\\d{6}\\s*,?", court_info_raw)
    post_code = re.findall("\\d{6}", court_info_raw)
    if len(court_info_agg) == 2 and len(post_code) == 1:
        address: str = f"{post_code[0]}, {court_info_agg[1]}"
        chosen_court: CourtInfo = CourtInfo(name=court_info_agg[0], address=address, note="")
        await state.update_data(chosen_court=chosen_court)
        await HeadPart.waiting_for_employer_name.set()
        await message.answer("Введите название организации и её ИНН, в которой вы работаете. "
                             "Если не знаете ИНН, введите просто название.\n"
                             "Например: OOO \"Рога и Копыта\" (ИНН 555555555555)")


async def court_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    chosen_option_index: int = int(callback_query.data.split(" ")[1])
    user_data = await state.get_data()
    court_info: List[CourtInfo] = user_data["court_info"]
    chosen_court: CourtInfo = court_info[chosen_option_index]
    await callback_query.answer(text=f"Суд '{chosen_court.name}' выбран.", show_alert=True)
    await state.update_data(chosen_court=chosen_court)
    await HeadPart.waiting_for_employer_name.set()
    await callback_query.message.answer("Введите название организации и её ИНН, в которой вы работаете. "
                                        "Если не знаете ИНН, введите просто название.\n"
                                        "Например: OOO \"Рога и Копыта\" (ИНН 555555555555)")


async def employer_name_chosen(message: types.Message, state: FSMContext):
    employer_name_raw: Optional[str] = message.text
    employer_name = re.sub("\\(ИНН \\d{12}\\)", "", employer_name_raw).strip()
    await state.update_data(chosen_employer_name=employer_name)

    inn_match = re.search("\\d{12}", employer_name_raw)
    if inn_match is not None:
        await state.update_data(inn=inn_match.group(0))

    await HeadPart.waiting_for_employer_address.set()
    await message.reply("Принято товарищ! А теперь введи адрес организации, в которой вы работаете. "
                        "Например: 101002, г. Любой, ул. Любая, д.4",
                        reply_markup=ReplyKeyboardRemove())


async def employer_address_chosen(message: types.Message, state: FSMContext):
    employer_address: Optional[str] = message.text
    await state.update_data(chosen_employer_address=employer_address)
    user_data = await state.get_data()
    # TODO: print entered data for checking?
    await message.answer("Данные раздела 'шапка' успешно заполнены.")
    user_id = message.from_user.id
    repository: Repository = Repository()
    claim_data: Optional[dict] = repository.get_claim_data(user_id)
    head_data: dict = {
        "claim_data.head": user_data
    }
    repository.update_record("claim-data", claim_data["_id"], head_data)
    await state.finish()
    claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb(message.from_user.id)
    await message.answer("Выберите часть искового заявления для заполнения", reply_markup=claim_parts_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(header_start, filters.Regexp(f"^{emojis.top_hat} шапка$"))
    dp.register_message_handler(user_name_chosen, state=HeadPart.waiting_for_user_name)
    dp.register_message_handler(post_code_chosen, state=HeadPart.waiting_for_user_post_code)
    dp.register_message_handler(city_chosen, state=HeadPart.waiting_for_user_city)
    dp.register_message_handler(street_chosen, state=HeadPart.waiting_for_user_street)
    dp.register_message_handler(house_chosen, state=HeadPart.waiting_for_user_house)
    dp.register_message_handler(apartment_chosen, state=HeadPart.waiting_for_user_apartment)
    dp.register_message_handler(option_chosen, state=HeadPart.waiting_for_option_chosen)
    dp.register_message_handler(court_entered, state=HeadPart.waiting_for_court_entered)
    dp.register_callback_query_handler(
        court_chosen,
        filters.Text(startswith="option"),
        state=HeadPart.waiting_for_court_chosen
    )
    dp.register_message_handler(employer_name_chosen, state=HeadPart.waiting_for_employer_name)
    dp.register_message_handler(employer_address_chosen, state=HeadPart.waiting_for_employer_address)
