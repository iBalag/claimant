from calendar import monthrange
from datetime import datetime
from typing import Tuple

WORK_DAYS_PER_MONTH: int = 20


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


def calc_first_month_days_oof(day: int, weekday: int, months_days: int):
    days_off: int = 0
    for d in range(day, months_days + 1):
        if weekday < 5:
            days_off = days_off + 1
        weekday = weekday + 1
        if weekday == 7:
            weekday = 0
    return days_off


def calc_oof_profit(start_oof_date: datetime, current_date: datetime, avr_salary: float) -> Tuple[float, int, int, int]:
    avr_payment_day = avr_salary / WORK_DAYS_PER_MONTH
    months_diff: int = calc_months_diff(start_oof_date, current_date)
    if months_diff > 0:
        _, first_oof_month_days = monthrange(start_oof_date.year, start_oof_date.month)
        first_month_days_off: int = calc_first_month_days_oof(start_oof_date.day, start_oof_date.weekday(),
                                                              first_oof_month_days)
        oof_days = months_diff * WORK_DAYS_PER_MONTH + first_month_days_off
    else:
        oof_days = calc_first_month_days_oof(start_oof_date.day, start_oof_date.weekday(),
                                             current_date.day)
    oof_profit = oof_days * avr_payment_day
    return round(oof_profit, 2), oof_days, months_diff, first_month_days_off
