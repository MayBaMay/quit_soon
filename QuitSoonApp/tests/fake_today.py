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
