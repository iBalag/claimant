from typing import List, Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from keyboards import emojis, get_claim_parts_kb
from repository import Repository

example_btn = KeyboardButton(f"{emojis.dna} {emojis.red_question_mark} показать пример")
chose_option_btn = KeyboardButton(f"{emojis.dna} {emojis.card_file_box} выбрать из списка")
essence_kb = ReplyKeyboardMarkup(resize_keyboard=True)
essence_kb.row(example_btn, chose_option_btn)


class EssencePart(StatesGroup):
    waiting_for_user_action = State()
    waiting_for_option_chosen = State()


async def essence_start(message: types.Message):
    await EssencePart.waiting_for_user_action.set()
    await message.reply("Опишите суть нарушения. "
                        "Введите, почему вы считаете, что ваши права нарушают. "
                        "Или выберите одну из следующий опций.",
                        reply_markup=essence_kb)


async def show_example(message: types.Message, state: FSMContext):
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    examples: Optional[List[str]] = repository.get_claim_tmp_examples(claim_theme, "essence")
    if examples is None or len(examples) == 0:
        await message.reply("Для данного шаблона не найдено примеров.")
        return

    for i, example in enumerate(examples):
        await message.reply(f"Пример №{i+1}: {example}")


async def options_selected(message: types.Message, state: FSMContext):
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, "essence")
    if options is None or len(options) == 0:
        await message.reply("Для данного шаблона не найдено опций для выбора.")
        return

    buttons = []
    for i, example in enumerate(options):
        option_btn: KeyboardButton = KeyboardButton(f"{i+1}")
        buttons.append(option_btn)
        await message.answer(f"№{i+1}: {example}")

    option_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup()
    option_kb.row(buttons)
    await EssencePart.waiting_for_option_chosen.set()
    await message.answer("Выберите одну из опций с помощью клавиатуры.")


async def option_chosen(message: types.Message, state: FSMContext):
    chosen_option_raw: Optional[str] = message.text
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    options: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, "essence")
    if chosen_option_raw is None or not chosen_option_raw.isdigit() \
            or int(chosen_option_raw) not in list(range(len(options) + 1)):
        buttons = []
        for i, _ in enumerate(options):
            option_btn: KeyboardButton = KeyboardButton(f"{i + 1}")
            buttons.append(option_btn)
        option_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup()
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

    await EssencePart.waiting_for_user_action.set()
    another_option_btn: KeyboardButton = KeyboardButton(f"{emojis.dna} {emojis.card_file_box} добавить еще опцию")
    enter_essence_btn: KeyboardButton = KeyboardButton(f"{emojis.dna} {emojis.pencil} добавить суть нарушения самостоятельно")
    compose_btn: KeyboardButton = KeyboardButton(f"{emojis.dna} {emojis.chequered_flag} закончить с сутью нарушения")
    next_actions_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup()
    next_actions_kb.add(another_option_btn)\
        .add(enter_essence_btn)\
        .add(compose_btn)

    await message.answer("Выберите дальнейшее действие с помощью клавиатуры", reply_markup=next_actions_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(essence_start, filters.Regexp(f"^{emojis.dna} суть нарушения"))
    dp.register_message_handler(show_example,
                                filters.Regexp(f"^{emojis.dna} {emojis.red_question_mark} показать пример"),
                                state=EssencePart.waiting_for_user_action)
    dp.register_message_handler(options_selected,
                                filters.Regexp(f"^{emojis.dna} {emojis.card_file_box} выбрать из списка"),
                                state=EssencePart.waiting_for_user_action)
    dp.register_message_handler(option_chosen,
                                filters.Regexp(f"^\\d+"),
                                state=EssencePart.waiting_for_option_chosen)