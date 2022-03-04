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
    # (
        # datetime(2022, 3, 4),
        # datetime(2022, 3, 4),
        # 20,
        # oof_profit_calculator.OOFCalculation(
            # oof_profit=1,
            # oof_days=1,
            # oof_months=0,
            # first_month_days_oof=1,
            # current_month_days_oof=1
        # )
    # ),
    (
        datetime(2022, 2, 4),
        datetime(2022, 3, 4),
        20,
        oof_profit_calculator.OOFCalculation(
            oof_profit=21,
            oof_days=21,
            oof_months=0,
            first_month_days_oof=17,
            current_month_days_oof=4
        )
    )
])
def test_calc_oof_profit(start_oof_date, current_date, avr_salary, expected_profit):
    assert expected_profit == oof_profit_calculator.calc_oof_profit(start_oof_date, current_date, avr_salary)

