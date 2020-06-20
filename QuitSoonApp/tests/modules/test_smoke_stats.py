#!/usr/bin/env python

"""Module testing smoke_stats module"""

import datetime
from datetime import date as real_date
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.tests import FakeTodayDate
from QuitSoonApp.models import UserProfile, Paquet, ConsoCig, Alternative, ConsoAlternative
from QuitSoonApp.modules import SmokeStats, HealthyStats

from ..MOCK_DATA import (
    Create_packs, Create_smoke,
    CreateAlternative, CreateConsoAlternative,
    row_paquet_data, row_conso_cig_data,
    row_alternative_data, row_conso_alt_data, fake_smoke
    )


class SmokeStatsTestCaseBigData(TestCase):
    """class testing Create_smoke """

    @mock.patch('datetime.date', FakeTodayDate)
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
        self.smoke = Create_smoke(self.user, row_conso_cig_data)
        self.smoke.populate_db()
        self.stats = SmokeStats(self.user, datetime.date.today())

    def test_get_nb_per_day_smoke(self):
        """test method get_nb_per_day_smoke"""
        self.assertEqual(self.stats.nb_per_day(datetime.date(2019, 9, 28)), 12)
        self.assertEqual(self.stats.nb_per_day(datetime.date(2019, 9, 22)), 0)

    def test_total_smoke(self):
        """test method total_smoke"""
        self.assertEqual(self.stats.total_smoke, 329)

    def test_average_per_day(self):
        """test method average_per_day"""
        self.assertEqual(round(self.stats.average_per_day), 5)

    def test_nb_jour_since_start(self):
        """test method nb_jour_since_start"""
        self.assertEqual(self.stats.nb_jour_since_start, 62)

    def test_count_smoking_day(self):
        """test method count_smoking_day"""
        self.assertEqual(self.stats.count_smoking_day, 57)

    def test_count_no_smoking_day(self):
        """test method count_no_smoking_day"""
        self.assertEqual(self.stats.count_no_smoking_day, 5)

    def test_total_cig_with_old_habits(self):
        """test method total_cig_with_old_habits"""
        self.assertEqual(self.stats.total_cig_with_old_habits, 1240)

    def test_nb_not_smoked_cig(self):
        """test method nb_not_smoked_cig"""
        self.assertEqual(self.stats.nb_not_smoked_cig, 911)

    def test_list_dates(self):
        """test method list_dates"""
        self.assertEqual(len(self.stats.list_dates), 62)
        self.assertEqual(self.stats.list_dates[0], datetime.date(2019, 9, 28))
        self.assertEqual(self.stats.list_dates[-1], datetime.date(2019, 11, 28))

    def test_no_smoking_day_list_dates(self):
        """test method no_smoking_day_list_dates"""
        self.assertEqual(
            self.stats.no_smoking_day_list_dates,
            [datetime.date(2019, 11, 22),
             datetime.date(2019, 11, 24),
             datetime.date(2019, 11, 26),
             datetime.date(2019, 11, 27),
             datetime.date(2019, 11, 28)]
             )

    def test_money_smoked_per_day(self):
        """test method money_smoked_per_day"""
        self.assertEqual(round(self.stats.money_smoked_per_day("2019-09-28"), 2), Decimal('5.61'))

    def test_average_money_per_day(self):
        """test method average_money_per_day"""
        self.assertEqual(round(self.stats.average_money_per_day, 2),  Decimal('2.55'))

    def test_total_money_smoked(self):
        self.assertEqual(self.stats.total_money_smoked, Decimal('157.91'))

    def test_total_money_with_starting_nb_cig(self):
        self.assertEqual(round(self.stats.total_money_with_starting_nb_cig, 2), Decimal('595.20'))

    def test_money_saved(self):
        self.assertEqual(self.stats.money_saved, Decimal('437.29'))


class SmokeStatsTestCaseSmallData(TestCase):
    """class testing Create_smoke """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.profile = UserProfile.objects.create(
            user=self.user,
            date_start="2020-06-19",
            starting_nb_cig=20
            )
        self.packs = Create_packs(self.user, row_paquet_data)
        self.packs.populate_db()
        self.smoke = Create_smoke(self.user, fake_smoke)
        self.smoke.populate_db()
        self.stats = SmokeStats(self.user, datetime.date(2020, 6, 20))

    def test_money_smoked_per_day(self):
        """test method money_smoked_per_day"""
        self.assertEqual(self.stats.money_smoked_per_day("2020-06-19"), 9.12)
        self.assertEqual(self.stats.money_smoked_per_day("2020-06-20"), 6.72)

    def test_total_cig_with_old_habits(self):
        """test method total_cig_with_old_habits"""
        self.assertEqual(self.stats.total_cig_with_old_habits, 40)

    def test_nb_not_smoked_cig(self):
        """test method nb_not_smoked_cig"""
        self.assertEqual(self.stats.nb_not_smoked_cig, 7)

    def test_average_money_per_day(self):
        """test method average_money_per_day"""
        self.assertEqual(self.stats.average_money_per_day, 7.92)

    def test_list_dates(self):
        """test method list_dates"""
        self.assertEqual(len(self.stats.list_dates), 2)
        self.assertEqual(
            self.stats.list_dates,
            [datetime.date(2020, 6, 19), datetime.date(2020, 6, 20)]
            )

    def test_total_money_smoked(self):
        self.assertEqual(self.stats.total_money_smoked, 15.84)

    def test_total_money_with_starting_nb_cig(self):
        self.assertEqual(self.stats.total_money_with_starting_nb_cig, 19.20)

    def test_money_saved(self):
        self.assertEqual(self.stats.money_saved,3.36)
        # self.assertEqual(stat.average_per_day, 200)

class HealthyStatsTestCase(TestCase):
    """class testing HealthyStats """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.profile = UserProfile.objects.create(
            user=self.user,
            date_start="2019-09-28",
            starting_nb_cig=20,
        )
        self.alternatives = CreateAlternative(self.user, row_alternative_data)
        self.alternatives.populate_db()
        self.healthy = CreateConsoAlternative(self.user, row_conso_alt_data)
        self.healthy.populate_db()
        self.stats = HealthyStats(self.user, datetime.date(2019, 11, 28))

    def test_min_per_day(self):
        self.assertEqual(self.stats.min_per_day(datetime.date(2019, 10, 19)), 155)

    def test_nicotine_per_day(self):
        self.assertEqual(self.stats.nicotine_per_day(datetime.date(2019, 10, 19)), 9)
