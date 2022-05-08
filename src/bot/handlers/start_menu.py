from datetime import datetime
from typing import List, Optional

import pytz
from aiogram import types, Dispatcher, filters
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from repository import Repository
from keyboards import get_start_menu_kb, get_claim_tmps_list_kb, get_claim_parts_kb, emojis
from statistics import collect_statistic, count_event


@collect_statistic(event_name="start:start_menu")
async def start_menu(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()
    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    await message.reply("Добрый день! Выберите одну из следующих команд:", reply_markup=start_menu_kb)


@collect_statistic(event_name="start:bot_info")
async def show_bot_info(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()

    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    bot_info: str = """
Это бот, который поможет вам составить исковое заявление в суд по нарушениям трудового законодательства.

Поддерживаемые команды:
/start - перейти в главное меню
/help - узнать информацию о боте
/choose_template - выбрать шаблон искового для заполнения
/sending - узнать про отправку искового
/tracking - узнать, как отслеживать исковое
/presentation - узнать, как выступать в суде

Мы должны предупредить вас об обработке персональных данных, в соответствии с ФЗ "О персональных данных". Если вы согласны, просто продолжайте работу с ботом в основном меню.

Зачем бот собирает данные: 
1. Чтобы заполнить ваши данные в исковом заявлении: фамилию, имя, отчество и адрес. Если вы не хотите указывать свои данные, можете указать любые, и потом исправить в итоговом файле вручную. 
2. Чтобы автоматически подобрать суд по вашему адресу. Если не хотите указывать свой адрес, вы можете указать любой и затем найти суд самостоятельно. 

Как бот хранит и уничтожает данные: ваши персональные данные будут храниться в зашифрованном виде в базе данных бота во время сессии заполнения заявления. 
Как только вы нажмёте кнопку "получить" - данные стираются полностью. Если вы выйдите из сессии, и при этом не нажмете кнопку "получить", данные также сотрутся автоматически через два часа.
    """
    infi_kb = InlineKeyboardMarkup(row_width=1)
    infi_kb.add(InlineKeyboardButton("Видеоинструкция к боту", url="https://www.youtube.com/watch?v=nNVZE0Ay8LQ"))
    await message.reply(bot_info, reply_markup=infi_kb)
    await message.answer("Выберите одну из следующих команд:", reply_markup=start_menu_kb)


@collect_statistic(event_name="start:choose_template")
async def choose_claim_tmp(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()

    claim_tmps_list_kb: ReplyKeyboardMarkup = get_claim_tmps_list_kb()
    await message.reply("Выберите один из шаблонов для заполнения", reply_markup=claim_tmps_list_kb)


async def choose_claim_part(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()

    temp_theme_raw: str = message.text
    temp_theme: str = temp_theme_raw.replace(emojis.page_facing_up, "").strip()
    repository: Repository = Repository()
    previous_claim_data: Optional[dict] = repository.get_claim_data(message.from_user.id, temp_theme)
    # This is the first time when the user chose the claim template.
    if previous_claim_data is None:
        new_claim_data: dict = {
            "user_id": message.from_user.id,
            "claim_theme": temp_theme,
            "created": datetime.utcnow().replace(tzinfo=pytz.UTC)
        }
        repository.insert_item("claim-data", new_claim_data)

        try:
            count_event(f"claim_template:{temp_theme}", message.from_user.id)
        except Exception as ex:
            print(f"Error occurred while collection statistics: {ex}")

    claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb(message.from_user.id)
    await message.reply("Выберите часть искового заявления для заполнения", reply_markup=claim_parts_kb)


@collect_statistic(event_name="start:claim_sending")
async def choose_claim_sending(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()

    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    claim_sanding_info: str = """
Чтобы подать заявление, нужно:

1. Уведомить ответчика.
По закону вы должны отправить копию искового заявления заказным письмом по адресу местонахождения вашего работодателя. Сохраните квитанцию об отправке - это важно. Копию квитанции приложите к исковому заявлению при подаче в суд.

2. Подать документы в суд. 
Это можно сделать тремя способами:
- Лично: распечатать исковое заявление в двух экземплярах, распечатать копии документов, которые вы указываете в приложении (оригиналы пусть будут у вас), и подать в экспедицию районного суда. На втором экземпляре вам поставят отметку о принятии.
- Через платформу ГАС «Правосудие» https://ej.sudrf.ru/ - документы подаются в электронном виде, зайти на платформу можно с вашей учетной записи на госуслугах.
- Заказным письмом по почте с уведомлением о вручении и описью вложения. Не самый надёжный способ, но так тоже можно.
"""
    await message.reply(claim_sanding_info, reply_markup=start_menu_kb)


@collect_statistic(event_name="start:claim_tracking")
async def choose_claim_tracking(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()

    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    claim_tracking_info: str = """
Отслеживать движение поданного заявления можно следующим образом:

- На сайте суда нужно найти ваше дело по фамилии или названию организации.
- Узнать номер дела и фамилию судьи.
- Узнать на какую дату и время назначено рассмотрение.
- Можно позвонить в канцелярию суда и попробовать узнать информацию о дате судебного заседания, но дозвониться бывает сложно.
- Как правило, первое заседание назначают спустя месяц после подачи документов, но может быть и раньше.
- В любом случае вам должны прислать повестку - следите за почтовым ящиком.
"""
    await message.reply(claim_tracking_info, reply_markup=start_menu_kb)


@collect_statistic(event_name="start:claim_presentation")
async def choose_court_presentation(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()

    start_menu_kb: ReplyKeyboardMarkup = get_start_menu_kb()
    court_appearance_info: str = """
Как вести себя в суде:

- Первым будет назначено предварительное заседание.
На этом заседании уточняются ваши требования и документы, которые вы прилагаете в подтверждение своих требований. 
- Если в подтверждение вашей позиции могут выступить
свидетели - обязательно заявите об этом на предварительном заседании.
- На предварительном заседании вам сообщат дату основного заседания.
- Если захотите приобщить к делу дополнительные материалы или пригласить свидетелей, лучше написать ходатайство об этом в письменном виде. Но можно это сделать устно, либо на предварительном заседании, либо в начале основного заседания. 
- Основное заседание строится так: сначала сторонам предлагают озвучить ходатайства, если они есть, потом предоставляют слово истцу, далее вопросы истцу от ответчика, потом слово предоставляется ответчику, далее вопросы ответчику от истца. После чего суд переходит к исследованию доказательств, приобщенных к материалам дела, далее прения - стороны высказываются дополнительно по тем моментам, которые они еще не озвучили. 
- Подготовьтесь к основному заседанию следующим образом: напишите себе речь на 2-3 минуты максимум. Чем короче и чётче вы озвучите свою позицию, тем лучше. Речь лучше запомнить. Строится она таким образом: сначала вы рассказываете хронологию событий (кратко), чем по вашему мнению нарушены ваши права и какие доказательства это подтверждают. Никакой лирики и историй из жизни. Что касается вопросов ответчику или ответов на его вопросы - помните, ваша задача не переспорить его, а показать суду, что ваша позиция адекватная и законная, а его - нет. 
- Если чувствуете, что процесс пошёл не туда, что вам нужно время или дополнительные доказательства, попросите отложить рассмотрение дела. Такое ходатайство вы можете аргументировать суду необходимостью приобщения дополнительных материалов. Но помните - суды крайне неохотно это делают, лучше подготовиться заранее.
"""
    await message.reply(court_appearance_info, reply_markup=start_menu_kb)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_menu, commands=["start"], state="*")
    dp.register_message_handler(start_menu, filters.Regexp(f"^{emojis.left_arrow} назад"))
    dp.register_message_handler(show_bot_info, filters.Regexp(f"(^{emojis.bookmark_tabs} узнать о боте$|/help)"))
    dp.register_message_handler(choose_claim_tmp, filters.Regexp(f"^{emojis.face_with_monocle} выбор иска|/choose_template"))
    dp.register_message_handler(choose_claim_tmp, filters.Regexp(f"^{emojis.left_arrow} к шаблонам"))
    dp.register_message_handler(choose_claim_sending,
                                filters.Regexp(f"^{emojis.incoming_envelope} подача заявления|/sending"))
    dp.register_message_handler(choose_claim_tracking,
                                filters.Regexp(
                                    f"^{emojis.magnifying_glass_tilted_left} отслеживание заявления|/tracking"))
    dp.register_message_handler(choose_court_presentation,
                                filters.Regexp(f"^{emojis.man_judge} выступление в суде|/presentation"))

    repository: Repository = Repository()
    tmp_names: List[str] = repository.get_tmps_list()
    tmp_regex: str = f"^{emojis.page_facing_up} ({'|'.join([tn for tn in tmp_names])})$"
    dp.register_message_handler(choose_claim_part, filters.Regexp(tmp_regex))
