from typing import List, Optional

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from keyboards import get_next_actions_kb, example_btn, get_claim_parts_kb
from repository import Repository

TERM_DISPLAY_NAME_MAP: dict = {
    "essence": "суть нарушения",
    "proofs": "доказательства"
}


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

    buttons = []
    for i, example in enumerate(options):
        option_btn: KeyboardButton = KeyboardButton(f"{i + 1}")
        buttons.append(option_btn)
        await message.answer(f"№{i + 1}: {example}")

    option_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    option_kb.row(*buttons)
    await state_groups.waiting_for_option_chosen.set()
    await message.answer("Выберите одну из опций с помощью клавиатуры.", reply_markup=option_kb)


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


async def claim_tmp_option_chosen(message: types.Message, state: FSMContext, claim_part: str, state_groups):
    chosen_option_raw: Optional[str] = message.text
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, claim_part)
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
    await message.answer("Опциональный вариант добавлен к сути нарушения.")

    await state_groups.waiting_for_user_action.set()
    next_actions_kb: ReplyKeyboardMarkup = get_next_actions_kb()
    await message.answer("Введите свой вариант самостоятельно. "
                         "Или выберите дальнейшее действие с помощью клавиатуры",
                         reply_markup=next_actions_kb)


async def show_claim_tmp_example(message: types.Message, claim_part):
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    examples: Optional[List[str]] = repository.get_claim_tmp_examples(claim_theme, claim_part)
    if examples is None or len(examples) == 0:
        await message.reply("Для данной части примеров не найдено.")
        await message.answer("Введите свой вариант самостоятельно. "
                             "Или выберите дальнейшее действие с помощью клавиатуры",)
        return

    for i, example in enumerate(examples):
        await message.reply(f"Пример №{i+1}: {example}")

    next_actions_kb: ReplyKeyboardMarkup = get_next_actions_kb()
    await message.answer("Введите свой вариант самостоятельно. "
                         "Или выберите дальнейшее действие с помощью клавиатуры",
                         reply_markup=next_actions_kb)
