#!/usr/bin/env python

"""Module testing smoke_stats module"""

import datetime
from datetime import date as real_date
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.tests import FakeTodayDate191128
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

    @mock.patch('datetime.date', FakeTodayDate191128)
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

    def test_total_smoke_all_days(self):
        """test method total_smoke_full_days"""
        self.assertEqual(self.stats.total_smoke_full_days, 329)

    def test_total_smoke_full_days(self):
        """test method total_smoke_full_days"""
        self.assertEqual(self.stats.total_smoke_full_days, 329)

    def test_average_per_day(self):
        """test method average_per_day"""
        self.assertEqual(round(self.stats.average_per_day), 5)

    def test_nb_jour_since_start(self):
        """test method nb_jour_since_start"""
        self.assertEqual(self.stats.nb_full_days_since_start, 61)

    def test_count_smoking_day(self):
        """test method count_smoking_day"""
        self.assertEqual(self.stats.count_smoking_day, 57)

    def test_count_no_smoking_day(self):
        """test method count_no_smoking_day"""
        self.assertEqual(self.stats.count_no_smoking_day, 4)

    def test_total_cig_with_old_habits(self):
        """test method total_cig_with_old_habits"""
        self.assertEqual(self.stats.total_cig_with_old_habits, 1220)

    def test_nb_not_smoked_cig_full_days(self):
        """test method nb_not_smoked_cig_full_days"""
        self.assertEqual(self.stats.nb_not_smoked_cig_full_days, 891)

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
        self.assertEqual(round(self.stats.money_smoked_per_day("2019-09-28"), 2), Decimal('5.66'))

    def test_average_money_per_day_full_days(self):
        """test method average_money_per_day_full_days"""
        self.assertEqual(round(self.stats.average_money_per_day_full_days, 2),  Decimal('2.61'))

    def test_total_money_smoked_full_days(self):
        self.assertEqual(self.stats.total_money_smoked_full_days, Decimal('159.155'))

    def test_total_money_with_starting_nb_cig(self):
        self.assertEqual(round(self.stats.total_money_with_starting_nb_cig, 2), Decimal('591.70'))

    def test_money_saved_full_days(self):
        self.assertEqual(self.stats.money_saved_full_days, Decimal('432.54'))


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

    def test_get_nb_per_day_smoke(self):
        """test method get_nb_per_day_smoke"""
        self.assertEqual(self.stats.nb_per_day("2020-06-19"), 19)
        self.assertEqual(self.stats.nb_per_day("2020-06-20"), 14)


    def test_money_smoked_per_day(self):
        """test method money_smoked_per_day"""
        self.assertEqual(self.stats.money_smoked_per_day("2020-06-19"), Decimal('9.22'))
        self.assertEqual(self.stats.money_smoked_per_day("2020-06-20"),  Decimal('6.79'))

    def test_total_cig_with_old_habits(self):
        """test method total_cig_with_old_habits"""
        self.assertEqual(self.stats.total_cig_with_old_habits, 20)

    def test_nb_not_smoked_cig_full_days(self):
        """test method nb_not_smoked_cig_full_days"""
        self.assertEqual(self.stats.nb_not_smoked_cig_full_days, 1)

    def test_average_money_per_day_full_days(self):
        """test method average_money_per_day_full_days"""
        self.assertEqual(self.stats.average_money_per_day_full_days, Decimal('9.215'))

    def test_list_dates(self):
        """test method list_dates"""
        self.assertEqual(len(self.stats.list_dates), 2)
        self.assertEqual(
            self.stats.list_dates,
            [datetime.date(2020, 6, 19), datetime.date(2020, 6, 20)]
            )

    def test_total_money_smoked_full_days(self):
        self.assertEqual(self.stats.total_money_smoked_full_days, Decimal('9.215'))

    def test_total_money_with_starting_nb_cig(self):
        self.assertEqual(self.stats.total_money_with_starting_nb_cig, Decimal('9.7'))

    def test_money_saved_full_days(self):
        self.assertEqual(self.stats.money_saved_full_days, Decimal('0.48'))
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

    def test_report_substitut_per_period(self):
        """test method report_substitut_per_period """
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19)), '2h35')
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), type='Lo'), '2h05')
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), period='week'), '3h35')
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), period='week', type='Sp'), '1h00')
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), period='month'), '13h28')
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), period='month', type='Sp'), '6h53')

        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), 'Su'), 2)
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), 'Su', type='PAST'), 1)
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), 'Su', period='week'), 3)
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), 'Su', period='week', type='PAST'), 2)
        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), 'Su', period='month', type='PAST'), 10)

        self.assertEqual(self.stats.report_substitut_per_period(datetime.date(2019, 10, 19), 'Adfqsfc', period='weekdgfa', type='Pdsf'), None)

    def test_convert_minutes_to_hours_min_str(self):
        """test method inutes_to_hours_min_str """
        self.assertEqual(self.stats.convert_minutes_to_hours_min_str(50), '50 minutes')
        self.assertEqual(self.stats.convert_minutes_to_hours_min_str(60), '1h00')
        self.assertEqual(self.stats.convert_minutes_to_hours_min_str(90), '1h30')
        self.assertEqual(self.stats.convert_minutes_to_hours_min_str(120), '2h00')

    def test_nicotine_per_day(self):
        """test method nicotine_per_day """
        self.assertEqual(self.stats.nicotine_per_day(datetime.date(2019, 10, 19)), 9)
