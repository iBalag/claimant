from calendar import monthrange
from collections import namedtuple
from datetime import datetime

PaymentOFFCalculation = namedtuple("PaymentOFFCalculation",
                                   [
                                       "payment_off_profit",
                                       "payment_off_days",
                                       "payment_off_months",
                                       "first_month_payment_off_days",
                                       "current_month_payment_off_days"]
                                   )
