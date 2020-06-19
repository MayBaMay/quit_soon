#!/usr/bin/env python

"""Test smoke-app module"""

import datetime
from datetime import datetime as dt
from unittest import mock

from django.test import TestCase
from django.contrib.auth.models import User
from QuitSoonApp.dash_apps.smoke_app import dataframe, get_user_infos_from_stats, stats

from QuitSoonApp.tests import FakeTodayDate
from QuitSoonApp.models import UserProfile, Paquet, ConsoCig, Alternative, ConsoAlternative
from QuitSoonApp.modules import SmokeStats, HealthyStats
from QuitSoonApp.tests.MOCK_DATA import (
    Create_packs, row_paquet_data,
    Create_smoke, row_conso_cig_data,
    )


class DataFrameTestCase(TestCase):

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.profile = UserProfile.objects.create(
            user=self.user,
            date_start="2019-09-28",
            starting_nb_cig=20,
        )
        self.packs = Create_packs(self.user, row_paquet_data)
        self.packs.populate_db()
        self.smokes = Create_smoke(self.user, row_conso_cig_data)
        self.smokes.populate_db()

    @mock.patch('datetime.date', FakeTodayDate)
    def test_stats(self):
        value = datetime.date.today()
        smoke, healthy = stats(self.user)
        self.assertIsInstance(smoke, SmokeStats)
        self.assertIsInstance(healthy, HealthyStats)
        self.assertEqual(smoke.nb_per_day(datetime.date(2019, 9, 28)), 12)
        self.assertEqual(len(smoke.list_dates), 62)

    def test_get_user_infos_from_stats(self):
        smoke = SmokeStats(self.user, datetime.date(2019, 11, 28))
        healthy = HealthyStats(self.user, datetime.date(2019, 11, 28))
        user_infos = get_user_infos_from_stats(smoke, healthy)
        self.assertEqual(len(user_infos), 5)
        for info in user_infos:
            self.assertEqual(len(user_infos[info]), 62)
        self.assertEqual(user_infos['nb_cig'][:20],
                         [12, 11, 10, 12, 1, 14, 8, 9, 6, 7, 7, 5, 6, 5, 8, 7, 6, 7, 6, 4])

    def test_dataframe(self):
        user_dict = {
            'date': [
                datetime.datetime(2020, 6, 5, 0, 0), datetime.datetime(2020, 6, 6, 0, 0),
                datetime.datetime(2020, 6, 7, 0, 0), datetime.datetime(2020, 6, 8, 0, 0),
                datetime.datetime(2020, 6, 9, 0, 0), datetime.datetime(2020, 6, 10, 0, 0),
                datetime.datetime(2020, 6, 11, 0, 0), datetime.datetime(2020, 6, 12, 0, 0),
                datetime.datetime(2020, 6, 13, 0, 0), datetime.datetime(2020, 6, 14, 0, 0),
                datetime.datetime(2020, 6, 15, 0, 0), datetime.datetime(2020, 6, 16, 0, 0),
                datetime.datetime(2020, 6, 17, 0, 0), datetime.datetime(2020, 6, 18, 0, 0),
                datetime.datetime(2020, 6, 19, 0, 0)
                ],
            'nb_cig': [9, 5, 0, 0, 0, 0, 0, 4, 0, 3, 0, 0, 0, 1, 1],
            'money_smoked': [3.78, 1.68, 0.0, 0.0, 0.0, 0.0, 0.0, 1.2, 0.0, 0.9, 0.0, 0.0, 0.0, 0.48, 0.48],
            'activity_duration': [0, 0, 0, 0, 0, 60, 0, 105, 0, 290, 0, 0, 0, 0, 0],
            'nicotine': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            }
        self.assertEqual(dataframe('D', user_dict).loc['05/06/20', 'nb_cig'], 9)
        self.assertEqual(dataframe('W', user_dict).loc['08/06/20-14/06/20', 'nb_cig'], 7)
        self.assertEqual(dataframe('M', user_dict).loc['06/20', 'nb_cig'], 23)
