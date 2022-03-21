from datetime import datetime
import pytest

import common.payoff_profit_calculator as payoff_profit_calculator


@pytest.mark.parametrize("payoff_date, payday, current_date, paydays_count", [
    (datetime(2018, 11, 1), 1, datetime(2018, 11, 28), 1),
    (datetime(2018, 11, 1), 1, datetime(2018, 12, 28), 2),
    (datetime(2018, 11, 10), 5, datetime(2018, 11, 28), 0),
    (datetime(2018, 11, 4), 5, datetime(2018, 12, 4), 1),
    (datetime(2018, 10, 4), 5, datetime(2019, 2, 1), 4),
    (datetime(2018, 10, 6), 5, datetime(2018, 11, 6), 1),
])
def test_get_paydays_count(payoff_date: datetime, payday: int, current_date: datetime, paydays_count: int):
    assert paydays_count == payoff_profit_calculator.calc_paydays_count(payoff_date, payday, current_date)
