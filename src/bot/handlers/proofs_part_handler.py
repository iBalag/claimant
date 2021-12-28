from typing import List, Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from keyboards import emojis, get_claim_parts_kb
from repository import Repository

chose_option_btn = KeyboardButton(f"{emojis.card_file_box} выбрать из списка")
proofs_kb = ReplyKeyboardMarkup(resize_keyboard=True)
proofs_kb.row(chose_option_btn)

another_option_btn: KeyboardButton = KeyboardButton(f"{emojis.card_file_box} добавить еще из списка")
compose_btn: KeyboardButton = KeyboardButton(f"{emojis.chequered_flag} закончить с доказательствами")
next_actions_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
next_actions_kb.add(another_option_btn) \
    .add(compose_btn)


class ProofsPart(StatesGroup):
    waiting_for_user_action = State()
    waiting_for_option_chosen = State()


async def proofs_start(message: types.Message):
    await ProofsPart.waiting_for_user_action.set()
    await message.reply("Укажите доказательства, которые подтверждают нарушение ваших прав. "
                        "Введите свой вариант или выберите одну из следующий опций из списка.",
                        reply_markup=proofs_kb)


async def action_selected(message: types.Message, state: FSMContext):
    option: Optional[str] = message.text
    if option.endswith("выбрать из списка") or option.endswith("добавить еще из списка"):
        await _process_option_selection(message)
        return
    if option.endswith("закончить с доказательствами"):
        await _process_proofs_end(message, state)
        return

    await _process_manual_enter(message, state)


async def option_chosen(message: types.Message, state: FSMContext):
    chosen_option_raw: Optional[str] = message.text
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, "proofs")
    if chosen_option_raw is None or not chosen_option_raw.isdigit() \
            or int(chosen_option_raw) not in list(range(len(options) + 1)):
        buttons = [KeyboardButton(f"{i + 1}") for i in range(len(options))]
        option_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
        option_kb.row(buttons)
        await message.answer("Выберите одну из опций с помощью клавиатуры.")
        return

    chosen_option: str = options[int(chosen_option_raw) - 1]
    user_data = await state.get_data()
    chosen_options: List[str]
    if "chosen_options" in user_data.keys():
        chosen_options = user_data["chosen_options"]
        chosen_options.append(chosen_option)
    else:
        chosen_options = [chosen_option]
    await state.update_data(chosen_options=chosen_options)
    await message.answer("Опциональный вариант добавлен к списку доказательств.")

    await ProofsPart.waiting_for_user_action.set()
    await message.answer("Укажите доказательства, которые подтверждают нарушение ваших прав. "
                         "Введите свой вариант или выберите одну из следующий опций из списка.",
                         reply_markup=next_actions_kb)


async def _process_option_selection(message: types.Message):
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, "proofs")
    if options is None or len(options) == 0:
        await ProofsPart.waiting_for_user_action.set()
        await message.reply("Для данного шаблона не найдено опций для выбора. "
                            "Укажите свой вариант самостоятельно", reply_markup=ReplyKeyboardRemove())
        return

    buttons = []
    for i, example in enumerate(options):
        option_btn: KeyboardButton = KeyboardButton(f"{i + 1}")
        buttons.append(option_btn)
        await message.answer(f"№{i + 1}: {example}")

    option_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    option_kb.row(*buttons)
    await ProofsPart.waiting_for_option_chosen.set()
    await message.answer("Выберите одну из опций с помощью клавиатуры.", reply_markup=option_kb)


async def _process_manual_enter(message: types.Message, state: FSMContext):
    manual_entered_proofs: str = message.text
    user_data = await state.get_data()
    chosen_options: List[str]
    if "chosen_options" in user_data.keys():
        chosen_options = user_data["chosen_options"]
        chosen_options.append(manual_entered_proofs)
    else:
        chosen_options = [manual_entered_proofs]
    await state.update_data(chosen_options=chosen_options)
    await message.answer("Свой вариант добавлен к списку доказательств.")
    await ProofsPart.waiting_for_user_action.set()
    await message.answer("Укажите доказательства, которые подтверждают нарушение ваших прав. "
                         "Введите свой вариант или выберите одну из следующий опций из списка.",
                         reply_markup=next_actions_kb)


async def _process_proofs_end(message: types.Message, state: FSMContext):
    await message.answer("Данные раздела 'доказательства' успешно заполнены.", reply_markup=ReplyKeyboardRemove())
    user_id = message.from_user.id
    user_data = await state.get_data()
    repository: Repository = Repository()
    claim_data: Optional[dict] = repository.get_claim_data(user_id)
    proofs_data: dict = {
        "claim_data.proofs": user_data
    }
    repository.update_record("claim-data", claim_data["_id"], proofs_data)
    await state.finish()
    claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb(message.from_user.id)
    await message.answer("Выберите часть искового заявления для заполнения", reply_markup=claim_parts_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(proofs_start, filters.Regexp(f"^{emojis.page_with_curl} доказательства"))
    dp.register_message_handler(action_selected, state=ProofsPart.waiting_for_user_action)
    dp.register_message_handler(option_chosen, filters.Regexp(f"^\\d+"), state=ProofsPart.waiting_for_option_chosen)
