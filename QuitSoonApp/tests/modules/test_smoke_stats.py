#!/usr/bin/env python

"""Module testing smoke_stats module"""

import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import UserProfile, Paquet, ConsoCig
from QuitSoonApp.modules import SmokeStats

from ..MOCK_DATA import (
    Create_test_packs, row_paquet_data,
    Create_test_smoke, row_conso_cig_data,
    )

class SmokeStatsTestCase(TestCase):
    """class testing Create_test_smoke """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.profile = UserProfile.objects.create(
            user=self.user,
            date_start="2019-09-28",
            starting_nb_cig=20
        )
        self.packs = Create_test_packs(self.user, row_paquet_data)
        self.packs.populate_test_db()
        self.smoke = Create_test_smoke(self.user, row_conso_cig_data)
        self.smoke.populate_test_db()
        self.stat = SmokeStats(self.user, datetime.date(2019, 11, 28))

    def test_get_missing_datas_smoke(self):
        self.assertEqual(self.stat.nb_per_day("2019-09-28"), 12)
        self.assertEqual(self.stat.nb_per_day("2019-09-22"), 0)

    def test_total_smoke(self):
        self.assertEqual(self.stat.total_smoke, 329)

    def test_average_per_day(self):
        self.assertEqual(self.stat.average_per_day, 5.306451612903226)

    def test_nb_jour_since_start(self):
        self.assertEqual(self.stat.nb_jour_since_start, 62)

    def test_count_smoking_day(self):
        self.assertEqual(self.stat.count_smoking_day, 57)

    def test_count_no_smoking_day(self):
        self.assertEqual(self.stat.count_no_smoking_day, 5)

    def test_no_smoking_day_list_dates(self):
        self.assertEqual(
            self.stat.no_smoking_day_list_dates,
            [datetime.date(2019, 11, 22),
             datetime.date(2019, 11, 24),
             datetime.date(2019, 11, 26),
             datetime.date(2019, 11, 27),
             datetime.date(2019, 11, 28)]
             )
        print(self.stat.total_money_smoked)
        print(self.stat.total_money_with_starting_nb_cig)
        print(self.stat.money_saved)
        # self.assertEqual(stat.average_per_day, 200)
