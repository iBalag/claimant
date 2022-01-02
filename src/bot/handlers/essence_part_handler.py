from typing import Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup

from handlers.common_actions_handlers import process_manual_enter, process_option_selection, \
    process_complete_part_editing, claim_tmp_option_chosen, show_claim_tmp_example
from keyboards import emojis, get_common_start_kb

CLAIM_PART: str = "essence"


class EssencePart(StatesGroup):
    waiting_for_user_action = State()
    waiting_for_option_chosen = State()


async def essence_start(message: types.Message):
    await EssencePart.waiting_for_user_action.set()
    start_kb: ReplyKeyboardMarkup = get_common_start_kb()
    await message.reply("Опишите суть нарушения. "
                        "Введите, почему вы считаете, что ваши права нарушают. "
                        "Или выберите одну из следующий опций.",
                        reply_markup=start_kb)


async def show_example(message: types.Message, state: FSMContext):
    await show_claim_tmp_example(message, CLAIM_PART)


async def action_selected(message: types.Message, state: FSMContext):
    option: Optional[str] = message.text
    if option.endswith("выбрать из списка") or option.endswith("добавить еще из списка"):
        await process_option_selection(message, CLAIM_PART, EssencePart)
        return
    if option.endswith("закончить заполнение"):
        await process_complete_part_editing(message, state, CLAIM_PART)
        return

    await process_manual_enter(message, state, EssencePart)


async def option_chosen(message: types.Message, state: FSMContext):
    await claim_tmp_option_chosen(message, state, CLAIM_PART, EssencePart)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(essence_start, filters.Regexp(f"^{emojis.key} суть нарушения"))
    dp.register_message_handler(show_example,
                                filters.Regexp(f"^{emojis.red_question_mark} показать пример"),
                                state=EssencePart.states)
    dp.register_message_handler(action_selected, state=EssencePart.waiting_for_user_action)
    dp.register_message_handler(option_chosen, filters.Regexp(f"^\\d+"), state=EssencePart.waiting_for_option_chosen)