from collections import namedtuple
from datetime import datetime, timedelta
from typing import Tuple, Optional

from .oof_profit_calculator import OOFCalculation, calc_months_diff
from .crb_client import get_key_rate

PayOffCalculation = namedtuple(
    "PayOffCalculation",
    [
        "payoff_profit",
        "compensation",
        "paydays_1_count",
        "paydays_2_count",
        "key_rate",
        "whole_days"
    ]
)


COMPENSATION_RATIO: float = 1 / 150


def calc_compensation(start_payoff_profit_date: datetime,
                      current_date: datetime, payoff_profit: float, key_rate) -> Tuple[float, int]:
    days_delta: timedelta = current_date - start_payoff_profit_date
    compensation: float = payoff_profit * ((key_rate / 100) * COMPENSATION_RATIO) * days_delta.days
    return round(compensation, 2), days_delta.days


def calc_paydays_count(payoff_date: datetime, payday: int, current_date: datetime) -> int:
    months_diff: int = calc_months_diff(payoff_date, current_date)
    first_month_payday: int = 1 if payoff_date.day <= payday else 0
    if months_diff == 0:
        return first_month_payday

    last_month_payday: int = 1 if current_date.day >= payday else 0
    if months_diff == 1:
        return first_month_payday + last_month_payday
    else:
        return first_month_payday + (months_diff - 1) + last_month_payday


def calc_payoff_profit(payoff_date: datetime, payday_1: int, payment_1: float, payday_2: int, payment_2: Optional[float],
                       current_date: datetime) -> PayOffCalculation:
    paydays_1_count: int = calc_paydays_count(payoff_date, payday_1, current_date)
    paydays_2_count: int
    if payday_2 == 0:
        paydays_2_count = 0
        payment_2 = 0
    else:
        paydays_2_count = calc_paydays_count(payoff_date, payday_2, current_date)
    payoff_profit: float = paydays_1_count * payment_1 + paydays_2_count * payment_2

    key_rate: float = get_key_rate()
    compensation, whole_days = calc_compensation(payoff_date, current_date, payoff_profit, key_rate)

    return PayOffCalculation(
        payoff_profit=payoff_profit,
        compensation=compensation,
        paydays_1_count=paydays_1_count,
        paydays_2_count=paydays_2_count,
        key_rate=key_rate,
        whole_days=whole_days
    )


