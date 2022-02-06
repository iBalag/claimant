from calendar import monthrange
from collections import namedtuple
from datetime import datetime

WORK_DAYS_PER_MONTH: int = 20

OOFCalculation = namedtuple("OOFCalculation",
                            ["oof_profit", "oof_days", "oof_months", "first_month_days_oof", "current_month_days_oof"])


def calc_months_diff(star_date: datetime, end_date: datetime) -> int:
    if end_date <= star_date:
        return 0

    year_diff = end_date.year - star_date.year
    if end_date.month < star_date.month:
        year_diff = year_diff - 1
        month_diff = (end_date.month + 12) - star_date.month
    else:
        month_diff = end_date.month - star_date.month

    return year_diff * 12 + month_diff


def calc_work_days_in_month(start_day: int, start_day_weekday: int, end_day: int):
    days_off: int = 0
    weekday = start_day_weekday
    for d in range(start_day, end_day + 1):
        if weekday < 5:
            days_off = days_off + 1
        weekday = weekday + 1
        if weekday == 7:
            weekday = 0
    return days_off


def calc_oof_profit(start_oof_date: datetime, current_date: datetime, avr_salary: float) -> OOFCalculation:
    avr_payment_day = avr_salary / WORK_DAYS_PER_MONTH
    months_diff: int = calc_months_diff(start_oof_date, current_date)
    oof_months = 0
    first_month_days_oof = 0
    if months_diff > 0:
        _, first_oof_month_days = monthrange(start_oof_date.year, start_oof_date.month)
        first_month_days_oof: int = calc_work_days_in_month(start_oof_date.day, start_oof_date.weekday(),
                                                            first_oof_month_days)
        current_month_first_day: datetime = datetime(current_date.year, current_date.month, 1)
        current_month_days_oof: int = calc_work_days_in_month(1, current_month_first_day.weekday(), current_date.day)
        oof_months = months_diff - 1
        oof_days = oof_months * WORK_DAYS_PER_MONTH + first_month_days_oof + current_month_days_oof
    else:
        current_month_days_oof = calc_work_days_in_month(start_oof_date.day, start_oof_date.weekday(),
                                                         current_date.day)
        oof_days = current_month_days_oof

    oof_profit = oof_days * avr_payment_day
    return OOFCalculation(
        oof_profit=round(oof_profit, 2),
        oof_days=oof_days,
        oof_months=oof_months,
        first_month_days_oof=first_month_days_oof,
        current_month_days_oof=current_month_days_oof
    )
