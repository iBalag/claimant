from typing import List, Optional

from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from common import telegram_calendar
from keyboards import emojis, get_claim_parts_kb
from repository import Repository

example_btn = KeyboardButton(f"{emojis.red_question_mark} показать пример")
example_kb = ReplyKeyboardMarkup(resize_keyboard=True)
example_kb.row(example_btn)


CLAIM_PART: str = "story"


class StoryPart(StatesGroup):
    waiting_for_start_work_date = State()
    waiting_for_end_work_date = State()
    waiting_for_user_position = State()
    waiting_for_user_salary = State()
    waiting_for_user_story_conflict = State()
    waiting_for_user_employer_discussion = State()
    waiting_for_user_story_details = State()


async def story_start(message: types.Message):
    await StoryPart.waiting_for_start_work_date.set()
    calendar_kb = telegram_calendar.create_calendar()
    await message.reply("Для заполнения фабулы для начала укажите дату с которой вы работали\\работаете в компании.",
                        reply_markup=calendar_kb)


async def start_work_date_entered(callback_query: types.CallbackQuery, state: FSMContext):
    is_date, start_work_date = await telegram_calendar.process_calendar_selection(callback_query)
    if is_date:
        await state.update_data(start_work_date=start_work_date)
        repository: Repository = Repository()
        claim_theme: Optional[str] = repository.get_current_claim_theme(callback_query.from_user.id)
        actions: Optional[List[str]] = repository.get_claim_tmp_actions(claim_theme, CLAIM_PART)
        if actions is not None and "enter_end_date" in actions:
            await StoryPart.waiting_for_end_work_date.set()
            calendar_kb = telegram_calendar.create_calendar()
            await callback_query.message.answer(
                "Далее укажите дату последнего отработанного дня в компании.",
                reply_markup=calendar_kb)
        else:
            await StoryPart.waiting_for_user_position.set()
            await callback_query.message.answer("Напишите, в какой точно должности вы работали. "
                                                "Можно посмотреть в трудовой книжке или трудовом договоре.",
                                                reply_markup=example_kb)


async def end_work_date_entered(callback_query: types.CallbackQuery, state: FSMContext):
    is_date, end_work_date = await telegram_calendar.process_calendar_selection(callback_query)
    if is_date:
        await state.update_data(end_work_date=end_work_date)
        await StoryPart.waiting_for_user_position.set()
        await callback_query.message.answer("Напишите, в какой точно должности вы работали. "
                                            "Можно посмотреть в трудовой книжке или трудовом договоре.",
                                            reply_markup=example_kb)


async def user_position_entered(message: types.Message, state: FSMContext):
    user_position: Optional[str] = message.text
    await state.update_data(user_position=user_position)
    await StoryPart.waiting_for_user_salary.set()
    await message.answer("Укажите, какой у вас был оклад.", reply_markup=example_kb)


async def user_salary_entered(message: types.Message, state: FSMContext):
    user_salary: Optional[str] = message.text
    await state.update_data(user_salary=user_salary)
    await StoryPart.waiting_for_user_story_conflict.set()
    await message.answer("Напишите, когда и почему у вас начался трудовой конфликт.", reply_markup=example_kb)


async def story_conflict_entered(message: types.Message, state: FSMContext):
    story_conflict: Optional[str] = message.text
    await state.update_data(story_conflict=story_conflict)
    await StoryPart.waiting_for_user_employer_discussion.set()
    await message.answer("Дальше опишите ваше общение с работодателем: как развивался конфликт, "
                         "какие действия совершали вы и работодатель. "
                         "Если добавить нечего - просто напишите 'нет'.", reply_markup=example_kb)


async def user_employer_discussion_entered(message: types.Message, state: FSMContext):
    user_employer_discussion: Optional[str] = message.text
    if user_employer_discussion is None or user_employer_discussion.lower() == "нет":
        user_employer_discussion = ""
    await state.update_data(user_employer_discussion=user_employer_discussion)
    await StoryPart.waiting_for_user_story_details.set()
    await message.answer("Если считаете важным, добавьте детали, например, что в этот момент "
                         "происходило в компании, как реагировали ваши коллеги. "
                         "Если добавить нечего - просто напишите 'нет'.", reply_markup=example_kb)


async def story_details_entered(message: types.Message, state: FSMContext):
    story_details: Optional[str] = message.text
    if story_details is None or story_details.lower() == "нет":
        story_details = ""

    await state.update_data(story_details=story_details)
    await message.answer("Данные раздела 'фабула' успешно заполнены.", reply_markup=ReplyKeyboardRemove())

    user_id = message.from_user.id
    user_data = await state.get_data()
    repository: Repository = Repository()
    claim_data: Optional[dict] = repository.get_claim_data(user_id)
    story_data: dict = {
        "claim_data.story": user_data
    }
    repository.update_record("claim-data", claim_data["_id"], story_data)
    await state.finish()
    claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb(message.from_user.id)
    await message.answer("Выберите часть искового заявления для заполнения", reply_markup=claim_parts_kb)


async def show_example(message: types.Message, state: FSMContext):
    repository: Repository = Repository()
    claim_theme: Optional[str] = repository.get_current_claim_theme(message.from_user.id)
    claim_tmp: Optional[dict] = repository.get_claim_tmp(claim_theme)
    story_examples: List[str]
    if claim_tmp is not None and "story" in claim_tmp.keys() and "examples" in claim_tmp["story"].keys():
        story_examples: List[str] = claim_tmp["story"]["examples"]
    else:
        await message.reply("Для данного шаблона не найдено примеров.")
        return

    current_state: Optional[str] = await state.get_state()
    example_index: Optional[int] = None
    if current_state == StoryPart.waiting_for_user_position.state:
        example_index = 0
    if current_state == StoryPart.waiting_for_user_story_conflict.state:
        example_index = 1
    if current_state == StoryPart.waiting_for_user_employer_discussion.state:
        example_index = 2
    if current_state == StoryPart.waiting_for_user_story_details.state:
        example_index = 3

    if example_index is None or example_index > (len(story_examples) - 1):
        await message.reply("Для данной части фабулы не найдено примера.")
        return

    example: str = story_examples[example_index]
    await message.reply(example)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(story_start, filters.Regexp(f"^{emojis.speech_balloon} фабула"))
    dp.register_message_handler(show_example,
                                filters.Regexp(f"^{emojis.red_question_mark} показать пример"),
                                state=StoryPart.states)
    dp.register_callback_query_handler(start_work_date_entered, state=StoryPart.waiting_for_start_work_date)
    dp.register_callback_query_handler(end_work_date_entered, state=StoryPart.waiting_for_end_work_date)
    dp.register_message_handler(user_position_entered, state=StoryPart.waiting_for_user_position)
    dp.register_message_handler(user_salary_entered, state=StoryPart.waiting_for_user_salary)
    dp.register_message_handler(story_conflict_entered, state=StoryPart.waiting_for_user_story_conflict)
    dp.register_message_handler(user_employer_discussion_entered, state=StoryPart.waiting_for_user_employer_discussion)
    dp.register_message_handler(story_details_entered, state=StoryPart.waiting_for_user_story_details)



