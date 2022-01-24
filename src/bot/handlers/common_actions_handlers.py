from calendar import monthrange
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup

from keyboards import get_next_actions_kb, example_btn, get_claim_parts_kb, emojis
from repository import Repository

TERM_DISPLAY_NAME_MAP: dict = {
    "essence": "суть нарушения",
    "proofs": "доказательства",
    "claims": "требования",
    "additions": "приложения"
}

WORK_DAYS_PER_MONTH: int = 20


async def process_manual_enter(message: types.Message, state: FSMContext, state_groups):
    manual_entered_value: str = message.text
    user_data = await state.get_data()
    chosen_options: List[str]
    if "chosen_options" in user_data.keys():
        chosen_options = user_data["chosen_options"]
        chosen_options.append(manual_entered_value)
    else:
        chosen_options = [manual_entered_value]

    await state.update_data(chosen_options=chosen_options)
    await message.answer("Свой вариант добавлен.")
    await state_groups.waiting_for_user_action.set()

    next_actions_kb: ReplyKeyboardMarkup = get_next_actions_kb()
    await message.answer("Введите свой вариант самостоятельно. "
                         "Или выберите дальнейшее действие с помощью клавиатуры",
                         reply_markup=next_actions_kb)


async def process_option_selection(message: types.Message, claim_part: str, state_groups):
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, claim_part)
    if options is None or len(options) == 0:
        await state_groups.waiting_for_user_action.set()
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row(example_btn)
        await message.reply("Для данного шаблона не найдено опций для выбора. "
                            "Введите свой вариант", reply_markup=kb)
        return

    options_kb = InlineKeyboardMarkup()
    options_text = []
    for i, option in enumerate(options):
        options_text.append(f"{i+1}. {option}")
        option_btn = InlineKeyboardButton(f"{i+1}", callback_data=f"option {i}")
        options_kb.insert(option_btn)
    options_kb.add(InlineKeyboardButton(f"{emojis.chequered_flag} завершить выбор опций",
                                        callback_data="complete options"))

    await state_groups.waiting_for_option_chosen.set()
    await message.answer("Выберите одну из опций:")
    await message.answer("\n".join(options_text), reply_markup=options_kb)


async def claim_tmp_option_chosen(callback_query: types.CallbackQuery, state: FSMContext, claim_part: str):
    chosen_option_index: int = int(callback_query.data.split(" ")[1])
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(callback_query.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, claim_part)
    chosen_option: str = options[chosen_option_index]

    user_data = await state.get_data()
    chosen_options: List[str]
    if "chosen_options" in user_data.keys():
        chosen_options = user_data["chosen_options"]
        if chosen_option not in chosen_options:
            chosen_options.append(chosen_option)
            await callback_query.answer(text="Опциональный вариант успешно добавлен.", show_alert=True)
        else:
            await callback_query.answer(text="Данная опция уже была добавлена ранее.", show_alert=True)
    else:
        chosen_options = [chosen_option]
        await callback_query.answer(text="Опциональный вариант успешно добавлен.", show_alert=True)

    await state.update_data(chosen_options=chosen_options)


async def show_claim_tmp_example(message: types.Message, claim_part):
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    examples: Optional[List[str]] = repository.get_claim_tmp_examples(claim_theme, claim_part)
    next_actions_kb: ReplyKeyboardMarkup = get_next_actions_kb()
    if examples is None or len(examples) == 0:
        await message.reply("Для данной части примеров не найдено.")
        await message.answer("Введите свой вариант самостоятельно. "
                             "Или выберите дальнейшее действие с помощью клавиатуры",
                             reply_markup=next_actions_kb)
        return

    claim_data = repository.get_claim_data(message.from_user.id, claim_theme)
    placeholders = get_placeholders(claim_data["claim_data"])
    for i, example in enumerate(examples):
        await message.reply(f"Пример №{i+1}: {example.format(**placeholders)}")

    await message.answer("Введите свой вариант самостоятельно. "
                         "Или выберите дальнейшее действие с помощью клавиатуры",
                         reply_markup=next_actions_kb)


async def process_complete_part_editing(message: types.Message, state: FSMContext, claim_part: str):
    display_name: str = TERM_DISPLAY_NAME_MAP[claim_part]
    await message.answer(f"Данные раздела '{display_name}' успешно заполнены.", reply_markup=ReplyKeyboardRemove())
    user_id = message.from_user.id
    user_data = await state.get_data()
    repository: Repository = Repository()
    claim_data: Optional[dict] = repository.get_claim_data(user_id)
    new_claim_data: dict = {
        f"claim_data.{claim_part}": user_data
    }
    repository.update_record("claim-data", claim_data["_id"], new_claim_data)
    await state.finish()
    claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb(message.from_user.id)
    await message.answer("Выберите часть искового заявления для заполнения", reply_markup=claim_parts_kb)


def get_placeholders(claim_data: dict) -> dict:
    placeholders: dict = {
        "start_work_date": claim_data["story"]["start_work_date"].strftime("%d.%m.%Y"),
        "salary": claim_data["story"]["user_salary"],
    }

    current_date: datetime = datetime.now()
    end_work_date = claim_data["story"]["end_work_date"]
    avr_salary = claim_data["story"].get("avr_salary")
    if end_work_date is not None and avr_salary is not None:
        placeholders["current_date"] = current_date.strftime("%d.%m.%Y")
        placeholders["avr_salary"] = avr_salary
        start_oof_date: datetime = end_work_date + timedelta(days=1)
        placeholders["start_oof_date"] = start_oof_date.strftime("%d.%m.%Y")
        oof_profit, oof_days = calc_oof_profit(start_oof_date, current_date, avr_salary)
        placeholders["oof_days"] = oof_days
        placeholders["oof_profit"] = oof_profit

    return placeholders


def calc_months_diff(star_date: datetime, end_date: datetime) -> int:
    if end_date <= star_date:
        return 0

    year_diff = end_date.year - star_date.year
    if end_date.month < star_date.month:
        year_diff = year_diff - 1
        month_diff = (end_date.month + 12) - star_date.month
    else:
        month_diff = end_date.month - star_date.month

    return year_diff * 12 + month_diff


def calc_first_month_days_oof(day: int, weekday: int, months_days: int):
    days_off: int = 0
    for d in range(day, months_days + 1):
        if weekday < 5:
            days_off = days_off + 1
        weekday = weekday + 1
        if weekday == 7:
            weekday = 0
    return days_off


def calc_oof_profit(start_oof_date: datetime, current_date: datetime, avr_salary: float) -> Tuple[float, int]:
    avr_payment_day = avr_salary / WORK_DAYS_PER_MONTH
    months_diff: int = calc_months_diff(start_oof_date, current_date)
    if months_diff > 0:
        _, first_oof_month_days = monthrange(start_oof_date.year, start_oof_date.month)
        first_month_days_off: int = calc_first_month_days_oof(start_oof_date.day, start_oof_date.weekday(),
                                                              first_oof_month_days)
        off_months: int = months_diff - 1
        oof_days = off_months * WORK_DAYS_PER_MONTH + first_month_days_off
    else:
        oof_days = calc_first_month_days_oof(start_oof_date.day, start_oof_date.weekday(),
                                             current_date.day)
    oof_profit = oof_days * avr_payment_day
    return round(oof_profit, 2), oof_days
