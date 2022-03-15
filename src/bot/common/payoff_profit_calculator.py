from collections import namedtuple
from datetime import datetime, timedelta
from typing import Tuple

from .oof_profit_calculator import OOFCalculation, calc_oof_profit
from .crb_client import get_key_rate

PayOffCalculation = namedtuple(
    "PayOffCalculation",
    [
        "payoff_profit",
        "compensation",
        "payoff_days",
        "payoff_months",
        "first_month_payoff_days",
        "current_month_payoff_days",
        "whole_days"
    ]
)


COMPENSATION_RATIO: float = 1 / 150


def calc_compensation(start_payoff_date: datetime, current_date: datetime, payoff_profit: float) -> Tuple[float, int]:
    days_delta: timedelta = current_date - start_payoff_date
    key_rate: float = get_key_rate()
    compensation: float = payoff_profit * ((key_rate / 100) * COMPENSATION_RATIO) * days_delta.days
    return round(compensation, 2), days_delta.days


def calc_payoff_profit(start_payoff_date: datetime, current_date: datetime, avr_salary: float) -> PayOffCalculation:
    # payoff profit calculation is equal to oof profit calculation
    oof_profit_calc: OOFCalculation = calc_oof_profit(start_payoff_date, current_date, avr_salary)
    compensation, whole_days = calc_compensation(start_payoff_date, current_date, oof_profit_calc.oof_profit)

    return PayOffCalculation(
        payoff_profit=oof_profit_calc.oof_profit,
        compensation=compensation,
        payoff_days=oof_profit_calc.oof_days,
        payoff_months=oof_profit_calc.oof_months,
        first_month_payoff_days=oof_profit_calc.first_month_days_oof,
        current_month_payoff_days=oof_profit_calc.current_month_days_oof,
        whole_days=whole_days
    )


