from typing import Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup

from handlers.common_actions_handlers import process_option_selection, process_complete_part_editing, \
    process_manual_enter, claim_tmp_option_chosen, show_claim_tmp_example
from keyboards import emojis, get_common_start_kb


CLAIM_PART: str = "proofs"


class ProofsPart(StatesGroup):
    waiting_for_user_action = State()
    waiting_for_option_chosen = State()


async def proofs_start(message: types.Message):
    await ProofsPart.waiting_for_user_action.set()
    start_kb: ReplyKeyboardMarkup = get_common_start_kb()
    await message.reply("Укажите доказательства, которые подтверждают нарушение ваших прав. "
                        "Введите свой вариант или выберите одну из следующий опций из списка.",
                        reply_markup=start_kb)


async def show_example(message: types.Message, state: FSMContext):
    await show_claim_tmp_example(message, CLAIM_PART)


async def action_selected(message: types.Message, state: FSMContext):
    option: Optional[str] = message.text
    if option.endswith("выбрать из списка") or option.endswith("добавить еще из списка"):
        await process_option_selection(message, CLAIM_PART, ProofsPart)
        return
    if option.endswith("закончить заполнение"):
        await process_complete_part_editing(message, state, CLAIM_PART)
        return

    await process_manual_enter(message, state, ProofsPart)


async def option_chosen(message: types.Message, state: FSMContext):
    await claim_tmp_option_chosen(message, state, CLAIM_PART, ProofsPart)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(proofs_start, filters.Regexp(f"^{emojis.page_with_curl} доказательства"))
    dp.register_message_handler(show_example,
                                filters.Regexp(f"^{emojis.red_question_mark} показать пример"),
                                state=ProofsPart.states)
    dp.register_message_handler(action_selected, state=ProofsPart.waiting_for_user_action)
    dp.register_message_handler(option_chosen, filters.Regexp(f"^\\d+"), state=ProofsPart.waiting_for_option_chosen)