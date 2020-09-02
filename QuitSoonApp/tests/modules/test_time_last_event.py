#!/usr/bin/env python

"""Module testing time_last_event module"""

import datetime
from dateutil import relativedelta
from unittest import mock
from freezegun import freeze_time
import pytz

from django.test import TestCase
from django.utils import timezone

from QuitSoonApp.modules import get_delta_last_event


class GetDeltaEventTestCase(TestCase):
    """class testing get_delta_last_event """

    @freeze_time("2020-06-20 10:00:00")
    def test_get_delta_last_event(self):
        self.assertEqual(timezone.now(), datetime.datetime(2020, 6, 20, 10, 0, tzinfo=pytz.utc))
        self.assertEqual(get_delta_last_event(datetime.datetime(2020, 6, 20, 10, 0, tzinfo=pytz.utc)), ['0 minute '])
        self.assertEqual(get_delta_last_event(datetime.datetime(2019, 5, 19, 9, 0, tzinfo=pytz.utc)), ['1 an ', '1 mois ', '1 jour ', '1 heure '])
        self.assertEqual(get_delta_last_event(datetime.datetime(2018, 4, 10, 0, 30, tzinfo=pytz.utc)), ['2 ans ', '2 mois ', '10 jours ', '9 heures ', '30 minutes '])
