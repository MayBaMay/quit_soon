#!/usr/bin/env python

"""Test smoke-app module"""

import datetime
from datetime import datetime as dt
from unittest import mock

from django.test import TestCase
from django.contrib.auth.models import User
from QuitSoonApp.dash_apps.graphs_app import dataframe, get_user_infos_from_stats, stats

from QuitSoonApp.tests import FakeTodayDate200621
from QuitSoonApp.models import UserProfile, Paquet, ConsoCig, Alternative, ConsoAlternative
from QuitSoonApp.modules import SmokeStats, HealthyStats
from QuitSoonApp.tests.MOCK_DATA import (
    Create_packs, row_paquet_data,
    Create_smoke, fake_smoke,
    )
from QuitSoonApp.dash_apps.smoke_time_app import generate_hour_df



class TimeAppTestCase(TestCase):

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.profile = UserProfile.objects.create(
            user=self.user,
            date_start="2020-06-19",
            starting_nb_cig=20,
        )
        self.packs = Create_packs(self.user, row_paquet_data)
        self.packs.populate_db()
        self.smokes = Create_smoke(self.user, fake_smoke)
        self.smokes.populate_db()

    @mock.patch('datetime.date', FakeTodayDate200621)
    def test_generate_hour_df(self):
        hour = generate_hour_df(self.user)
        print('hour',hour)
        self.assertEqual(round(hour.loc[9], 2), 0.5)
        self.assertEqual(round(hour.loc[14], 2), 1.0)
        self.assertEqual(round(hour.loc[17], 2), 1.5)
