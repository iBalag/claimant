from datetime import datetime, timedelta
from typing import Optional, List

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from handlers.common_actions_handlers import process_complete_part_editing
from keyboards import emojis, get_claim_parts_kb
from repository import Repository
from calendar import monthrange

CLAIM_PART: str = "claims"


class ClaimsPart(StatesGroup):
    waiting_for_annual_profit = State()
    waiting_for_optional_claim = State()


async def claims_start(message: types.Message, state: FSMContext):
    repository: Repository = Repository()
    claim_data: dict = repository.get_claim_data(message.from_user.id)
    required_parts: List[str] = ["head", "story"]
    if claim_data.get("claim_data") is None or \
            not any([part_name in claim_data["claim_data"].keys() for part_name in required_parts]):
        claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb(message.from_user.id)
        await message.reply("Пожалуйста, сперва заполните все разделы 'шапка' и 'фабула'.",
                            reply_markup=claim_parts_kb)
        return

    # TODO: add support of multiple options
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    actions: Optional[List[str]] = repository.get_claim_tmp_actions(claim_theme, CLAIM_PART)
    if actions is not None and "annual_profit" in actions:
        await ClaimsPart.waiting_for_annual_profit.set()
        await message.answer("Пожалуйста, укажите сколько вы заработали за последний год.",
                             reply_markup=ReplyKeyboardRemove())
        return

    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, CLAIM_PART)
    await process_claim_options(claim_theme, options, claim_data, message, state)


async def annual_profit_entered(message: types.Message, state: FSMContext):
    annual_profit_raw: Optional[str] = message.text
    if annual_profit_raw is None or annual_profit_raw.isdigit() is False:
        await message.reply("Заработок за прошлый год указан неверно. Попробуйте еще раз.")
        return
    annual_profit = float(annual_profit_raw)
    await state.update_data(annual_profit=annual_profit)

    repository: Repository = Repository()
    claim_data: dict = repository.get_claim_data(message.from_user.id)
    claim_data["claim_data"]["annual_profit"] = annual_profit

    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, CLAIM_PART)
    await process_claim_options(claim_theme, options, claim_data, message, state)


async def process_claim_options(claim_theme: str, options: Optional[List[str]], claim_data: dict,
                                message: types.Message, state: FSMContext):
    await message.reply(f"Основные требования для темы '{claim_theme}':", reply_markup=ReplyKeyboardRemove())
    placeholders = get_placeholders(claim_data["claim_data"])
    selected_options = []
    for i, option in enumerate(options):
        option = option.format(**placeholders)
        selected_options.append(option)
        await message.answer(f"{i + 1}. {option}")

    await state.update_data(claims=selected_options)

    # TODO: Add support of optional claim from list
    option_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    option_kb.insert(KeyboardButton("да")) \
        .insert(KeyboardButton("нет"))
    await ClaimsPart.waiting_for_optional_claim.set()
    await message.answer("Хотите добавить требование про взыскание морального вреда?", reply_markup=option_kb)


async def optional_claim_selected(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_options = user_data["claims"]
    option: Optional[str] = message.text
    if option.lower() == "да":
        selected_options.append("Взыскать с ответчика компенсацию за причиненный мне "
                                "моральный вред в размере 100 000 руб.")
        await state.update_data(claims=selected_options)

    await process_complete_part_editing(message, state, CLAIM_PART)


def get_placeholders(claim_data: dict) -> dict:
    end_work_date: datetime = claim_data["story"]["end_work_date"]
    start_oof_date: datetime = end_work_date + timedelta(days=1)
    current_date: datetime = datetime.now()
    placeholders: dict = {
        "defendant": claim_data["head"]["chosen_employer_name"],
        "position": claim_data["story"]["user_position"],
        "start_oof_date": start_oof_date.strftime("%d/%m/%Y"),
        "current_date": current_date.strftime("%d/%m/%Y"),
    }

    if "annual_profit" in claim_data.keys():
        placeholders["oof_profit"] = calc_oof_profit(start_oof_date, current_date,
                                                     claim_data["annual_profit"])
    return placeholders


def calc_oof_profit(start_oof_date: datetime, current_date: datetime, annual_profit: float) -> float:
    _, first_oof_month_days = monthrange(start_oof_date.year, start_oof_date.month)
    first_month_days_off: int = first_oof_month_days - start_oof_date.day
    avr_first_month_days_off: float = 29.3/first_oof_month_days * first_month_days_off
    off_months: int = current_date.month - start_oof_date.month - 1
    off_months = 0 if off_months == -1 else off_months
    avr_payment_day = (annual_profit/12)/29.3
    off_profit = ((off_months * 29.3) + avr_first_month_days_off) * avr_payment_day
    return round(off_profit, 2)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(claims_start, filters.Regexp(f"^{emojis.index_pointing_up} требования"))
    dp.register_message_handler(annual_profit_entered, state=ClaimsPart.waiting_for_annual_profit)
    dp.register_message_handler(optional_claim_selected, state=ClaimsPart.waiting_for_optional_claim)
