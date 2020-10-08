#!/usr/bin/env python

"""Base classes for models manager"""

import datetime
from datetime import timedelta
import pytz

from django.utils.timezone import make_aware


class BaseManager:
    """Base class for models manager"""

    def __init__(self, user, data):
        self.user = user
        self.data = data

    def get_request_data(self, data):
        """get data from dict passed as argument"""
        try:
            return self.data[data]
        except (KeyError, TypeError):
            return None


class ManagerConso(BaseManager):
    """Models manager with consumption (ConsoCig and ConsoAlternative)"""

    def __init__(self, user, data):
        BaseManager.__init__(self, user, data)

    @staticmethod
    def get_datetime_client_aware(date, time, tz_offset):
        """return in utc actual client datetime using tz_offset"""
        try:
            datetime_client = datetime.datetime.combine(date, time)
            datetime_client += timedelta(minutes=tz_offset)
            datetime_client = make_aware(datetime_client, pytz.utc)
            return datetime_client
        except TypeError:
            # get_request_data returned None
            return None
