from typing import Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup

from handlers.common_actions_handlers import process_option_selection, process_complete_part_editing, \
    process_manual_enter, claim_tmp_option_chosen, show_claim_tmp_example
from keyboards import emojis, get_common_start_kb, get_next_actions_kb
from statistics import collect_statistic

CLAIM_PART: str = "proofs"


class ProofsPart(StatesGroup):
    waiting_for_user_action = State()
    waiting_for_option_chosen = State()


@collect_statistic(event_name="proofs:start")
async def proofs_start(message: types.Message, state: FSMContext):
    await ProofsPart.waiting_for_user_action.set()
    start_kb: ReplyKeyboardMarkup = get_common_start_kb()
    await message.reply("Укажите доказательства, которые подтверждают нарушение ваших прав. "
                        "Введите свой вариант или выберите одну из следующий опций из списка.",
                        reply_markup=start_kb)


@collect_statistic(event_name="proofs:show_example")
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


async def option_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    await claim_tmp_option_chosen(callback_query, state, CLAIM_PART)


async def finish_option_choosing(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await ProofsPart.waiting_for_user_action.set()
    next_actions_kb: ReplyKeyboardMarkup = get_next_actions_kb()
    await callback_query.message.answer("Введите свой вариант самостоятельно. "
                                        "Или выберите дальнейшее действие с помощью клавиатуры",
                                        reply_markup=next_actions_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(proofs_start, filters.Regexp(f"^{emojis.page_with_curl} доказательства"))
    dp.register_message_handler(show_example,
                                filters.Regexp(f"^{emojis.red_question_mark} показать пример"),
                                state=ProofsPart.states)
    dp.register_message_handler(action_selected, state=ProofsPart.waiting_for_user_action)
    dp.register_callback_query_handler(
        option_chosen,
        filters.Text(startswith="option"),
        state=ProofsPart.waiting_for_option_chosen
    )

    dp.register_callback_query_handler(finish_option_choosing,
                                       filters.Text(equals="complete options"),
                                       state=ProofsPart.waiting_for_option_chosen)
