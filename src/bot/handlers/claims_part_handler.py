from typing import Optional, List

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from handlers.common_actions_handlers import process_complete_part_editing
from keyboards import emojis
from repository import Repository

CLAIM_PART: str = "claims"


class ClaimsPart(StatesGroup):
    waiting_for_optional_claim = State()


async def claims_start(message: types.Message):
    # Show main claims
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, CLAIM_PART)
    await message.reply(f"Основные требования для темы '{claim_theme}':", reply_markup=ReplyKeyboardRemove())
    for i, option in enumerate(options):
        await message.answer(f"{i+1}. {option}")

    # TODO: Add support of optional claim from list
    option_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    option_kb.insert(KeyboardButton("да"))\
             .insert(KeyboardButton("нет"))
    await ClaimsPart.waiting_for_optional_claim.set()
    await message.answer("Хотите добавить требование про взыскание морального вреда?", reply_markup=option_kb)


async def optional_claim_selected(message: types.Message, state: FSMContext):
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, CLAIM_PART)

    option: Optional[str] = message.text
    if option.lower() == "да":
        options.append("Взыскать с ответчика компенсацию за причиненный мне моральный вред в размере 100 000 руб.")
        await state.update_data(claims=options)

    await process_complete_part_editing(message, state, CLAIM_PART)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(claims_start, filters.Regexp(f"^{emojis.index_pointing_up} требования"))
    dp.register_message_handler(optional_claim_selected, state=ClaimsPart.waiting_for_optional_claim)
