import datetime
import calendar

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CALENDAR_CALLBACK = "CALENDAR"


def separate_callback_data(data):
    """ Separate the callback data"""
    return data.split(";")


def create_callback_data(action, year, month, day):
    """ Create the callback data associated to each button"""
    return CALENDAR_CALLBACK + ";" + ";".join([action, str(year), str(month), str(day)])


def create_calendar(year=None, month=None):
    """
    Create an inline keyboard with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns the InlineKeyboardMarkup object with the calendar.
    """
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = InlineKeyboardMarkup()
    # First row - Month and Year

    row = [
        InlineKeyboardButton("<", callback_data=create_callback_data("PREV-YEAR", year, month, 1)),
        InlineKeyboardButton(text=f"{calendar.month_name[month]} {str(year)}", callback_data=data_ignore),
        InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-YEAR", year, month, 1))
    ]
    keyboard.row(*row)
    # Second row - Week Days
    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row.append(InlineKeyboardButton(day, callback_data=data_ignore))
    keyboard.row(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                day_str = str(day)
                row.append(InlineKeyboardButton(day_str, callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.row(*row)
    # Last row - Buttons
    row = [
        InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, 1)),
        InlineKeyboardButton(" ", callback_data=data_ignore),
        InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day))
    ]
    keyboard.row(*row)

    return keyboard


async def process_calendar_selection(query: types.CallbackQuery):
    """
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    """
    ret_data = (False, None)
    (_, action, year, month, day) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        await query.bot.answer_callback_query(callback_query_id=query.id)
    elif action == "PREV-YEAR":
        pre = curr - datetime.timedelta(days=365)
        await query.bot.edit_message_text(text=query.message.text,
                                          chat_id=query.message.chat.id,
                                          message_id=query.message.message_id,
                                          reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == "NEXT-YEAR":
        ne = curr + datetime.timedelta(days=365)
        await query.bot.edit_message_text(text=query.message.text,
                                          chat_id=query.message.chat.id,
                                          message_id=query.message.message_id,
                                          reply_markup=create_calendar(int(ne.year), int(ne.month)))
    elif action == "DAY":
        ret_data = True, datetime.datetime(int(year), int(month), int(day))
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        await query.bot.edit_message_text(text=query.message.text,
                                          chat_id=query.message.chat.id,
                                          message_id=query.message.message_id,
                                          reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        await query.bot.edit_message_text(text=query.message.text,
                                          chat_id=query.message.chat.id,
                                          message_id=query.message.message_id,
                                          reply_markup=create_calendar(int(ne.year), int(ne.month)))
    else:
        await query.bot.answer_callback_query(callback_query_id=query.id, text="Something went wrong!")
        # UNKNOWN
    return ret_data
