""" module overriding datetime.date.today for tests"""

import datetime
from datetime import date as real_date
from datetime import datetime as real_datetime


class FakeTodayDate191128(datetime.date):
    "Override instancecheck so that a mock instance looks like a real date."
    class FakeDateType(type):
        "Used to ensure that isinstance(datetime.date, FakeDate3) returns True."
        def __instancecheck__(self, instance):
            return isinstance(instance, real_date)
    # this forces the FakeDate to return True to the isinstance date check
    __metaclass__ = FakeDateType
    @classmethod
    def today(cls):
        return cls(2019, 11, 28)

# class FakeTodayDate2(datetime.date):
#     "Mock out the today method, but return a real date instance."
#     def __new__(cls, *args, **kwargs):
#         return real_date.__new__(real_date, *args, **kwargs)
#
#     @classmethod
#     def today(cls):
#         return cls(2019, 11, 28)
#
# class FakeTodayDate3(datetime.date):
#     "Mock out the today method to return a fixed date."
#     @classmethod
#     def today(cls):
#         return cls(2000, 1, 1)

class FakeTodayDate200621(datetime.date):
    "Override instancecheck so that a mock instance looks like a real date."
    class FakeDateType(type):
        "Used to ensure that isinstance(datetime.date, FakeDate3) returns True."
        def __instancecheck__(self, instance):
            return isinstance(instance, real_date)
    # this forces the FakeDate to return True to the isinstance date check
    __metaclass__ = FakeDateType
    @classmethod
    def today(cls):
        return cls(2020, 6, 21)
