from datetime import datetime
import pytest;

import common.oof_profit_calculator as oof_profit_calculator

@pytest.mark.parametrize("start_date, end_date, month_between", [
    (datetime(2018, 11, 28), datetime(2018, 11, 28), 0),
    (datetime(2018, 12, 1), datetime(2018, 12, 31), 0),
    (datetime(2018, 10, 28), datetime(2018, 11, 28), 1),
    (datetime(2018, 10, 31), datetime(2018, 11, 1), 1),
    (datetime(2017, 11, 28), datetime(2018, 11, 28), 12),
    (datetime(2017, 12, 31), datetime(2018, 1, 1), 1)
])
def test_calc_months_diff(start_date, end_date, month_between):
    assert month_between == oof_profit_calculator.calc_months_diff(start_date, end_date)

# monday is 0, sunday is 6
@pytest.mark.parametrize("start_day, start_day_weekday, end_day, expected_result", [
    (1, 0, 28, 20),
    (1, 0, 31, 23),
    (1, 0, 30, 22),
    (1, 5, 30, 20),
    (1, 5, 31, 21),
    (1, 6, 31, 22),
    (1, 6, 30, 21),
    (1, 5, 2, 0),
    (1, 5, 2, 0),
    (20, 2, 26, 5),
    (20, 2, 27, 6),
])
def test_calc_work_days_in_month(start_day: int, start_day_weekday: int, end_day: int, expected_result: int):
    assert expected_result == oof_profit_calculator.calc_work_days_in_month(start_day, start_day_weekday, end_day)

@pytest.mark.parametrize("start_oof_date, current_date, avr_salary, expected_profit", [
    (
        datetime(2022, 3, 4),
        datetime(2022, 3, 4),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=1,
            oof_days=1,
            oof_months=0,
            first_month_days_oof=0,
            current_month_days_oof=1
        )
    ),
    (
        datetime(2022, 2, 1),
        datetime(2022, 2, 28),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=20,
            oof_days=20,
            oof_months=0,
            first_month_days_oof=0,
            current_month_days_oof=20
        )
    ),
    (
        datetime(2022, 2, 1),
        datetime(2022, 3, 31),
        40,
        oof_profit_calculator.OOFCalculation(
            oof_profit=86,
            oof_days=43,
            oof_months=0,
            first_month_days_oof=20,
            current_month_days_oof=23
        )
    ),
    (
        datetime(2021, 12, 1),
        datetime(2022, 2, 28),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=63,
            oof_days=63,
            oof_months=1,
            first_month_days_oof=23,
            current_month_days_oof=20
        )
    ),
    (
        datetime(2021, 11, 1),
        datetime(2022, 2, 28),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=82,
            oof_days=82, # number of days is 86, but we take the average for months in between
            oof_months=2,
            first_month_days_oof=22,
            current_month_days_oof=20
        )
    ),
    (
        datetime(2021, 10, 1),
        datetime(2022, 2, 28),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=101,
            oof_days=101, # number of days is 103, but we take the average for months in between
            oof_months=3,
            first_month_days_oof=21,
            current_month_days_oof=20
        )
    ),
    (
        datetime(2022, 1, 1),
        datetime(2022, 3, 31),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=64,
            oof_days=64,
            oof_months=1,
            first_month_days_oof=21,
            current_month_days_oof=23
        )
    ),
    (
        datetime(2021, 12, 1),
        datetime(2022, 1, 31),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=44,
            oof_days=44,
            oof_months=0,
            first_month_days_oof=23,
            current_month_days_oof=21
        )
    ),
    (
        datetime(2022, 1, 1),
        datetime(2022, 2, 28),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=41,
            oof_days=41,
            oof_months=0,
            first_month_days_oof=21,
            current_month_days_oof=20
        )
    )
])
def test_calc_oof_profit(start_oof_date, current_date, avr_salary, expected_profit):
    assert expected_profit == oof_profit_calculator.calc_oof_profit(start_oof_date, current_date, avr_salary)

