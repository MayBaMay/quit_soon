#!/usr/bin/env python

"""Module testing stats_manager module"""

import datetime
from datetime import date as real_date
import pytz
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from QuitSoonApp.models import UserProfile, Paquet, ConsoCig, Alternative, ConsoAlternative
from QuitSoonApp.modules import Stats, SmokeStats, HealthyStats

from ..MOCK_DATA import (
    Create_packs, Create_smoke,
    CreateAlternative, CreateConsoAlternative,
    row_paquet_data, row_conso_cig_data,
    row_alternative_data, row_conso_alt_data, fake_smoke
    )


class SmokeStatsTestCaseBigData(TestCase):
    """class testing Create_smoke """

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
        self.stats = SmokeStats(self.user, make_aware(datetime.datetime(2019, 11, 28, 12, 0), pytz.utc), -120)

    def test_user_no_profile(self):
        """test create stats while user didn't create a profile"""
        user = User.objects.create_user(
            'testuser', 'testfsdF@test.com', 'testpassword')
        stats = SmokeStats(user, make_aware(datetime.datetime(2019, 11, 28, 12, 0), pytz.utc), -120)
        self.assertEqual(stats.starting_nb_cig, 0)

    def test_get_aware_last_day(self):
        """test get last day including client tz_offset"""
        stats_no_tz = SmokeStats(self.user, make_aware(datetime.datetime(2019, 11, 28, 12, 0), pytz.utc), 0)
        self.assertEqual(stats_no_tz.tz_offset, 0)
        self.assertEqual(stats_no_tz.lastday, make_aware(datetime.datetime(2019, 11, 28, 12, 0)))

    def test_get_datetime_start_with_profile(self):
        """test get sarting app datetime including tz_offset"""
        self.assertEqual(self.stats.datetime_start, make_aware(datetime.datetime(2019, 9, 28, 11, 0), pytz.utc))

    def test_get_datetime_start_no_profile(self):
        """test get datetime while user didn't create a profile but saved a conso"""
        user = User.objects.create_user(
            'testuser', 'testdfqdsfq@test.com', 'testpassword')
        db_pack= Paquet.objects.create(
            user=user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        db_smoke = ConsoCig.objects.create(
            user=user,
            datetime_cig=datetime.datetime(2019, 9, 16, 10, 15, tzinfo=pytz.utc),
            paquet=db_pack,
            )
        stats = SmokeStats(user, make_aware(datetime.datetime(2019, 11, 28, 12, 0), pytz.utc), -120)
        self.assertEqual(stats.datetime_start, make_aware(datetime.datetime(2019, 9, 16, 12, 15), pytz.utc))

    def test_nb_full_period_for_average(self):
        """test method calculating nb_full periods in order to calculate average"""
        self.assertEqual(self.stats.nb_full_period_for_average(datetime.date(2019,11,28), 'day'), 61)
        self.assertEqual(self.stats.nb_full_period_for_average(datetime.date(2019,11,28), 'week'), 8)
        self.assertEqual(self.stats.nb_full_period_for_average(datetime.date(2019,11,28), 'month'), 1)
        self.assertEqual(self.stats.nb_full_period_for_average(datetime.date(2020,8,5), 'day'), 312)
        self.assertEqual(self.stats.nb_full_period_for_average(datetime.date(2020,8,5), 'week'), 44)
        self.assertEqual(self.stats.nb_full_period_for_average(datetime.date(2020,8,5), 'month'), 10)

    def test_nb_full_period_for_average_dates_first_and_last_day_of_month(self):
        """test method nb_full_period_for_average with complex dates"""
        user = User.objects.create_user(
            'OtherUser', 'newemail@test.com', 'testpassword')
        profile = UserProfile.objects.create(
            user=user,
            date_start="2019-12-01",
            starting_nb_cig=20,
        )
        stats = SmokeStats(user, make_aware(datetime.datetime(2019, 2, 1, 12, 0), pytz.utc), -120)
        self.assertEqual(stats.nb_full_period_for_average(datetime.date(2020, 2, 1), 'day'), 62)
        self.assertEqual(stats.nb_full_period_for_average(datetime.date(2020, 2, 1), 'week'), 8)
        self.assertEqual(stats.nb_full_period_for_average(datetime.date(2020, 2, 1), 'month'), 2)

    def test_update_models_dt_user(self):
        """test method update_dt_user_model_field with actual timedelta tz_offset"""
        conso = ConsoCig.objects.get(user=self.user, datetime_cig=datetime.datetime(2019, 9, 28, 9, 0, tzinfo=pytz.utc))
        self.assertEqual(conso.user_dt, datetime.datetime(2019, 9, 28, 11, 0, tzinfo=pytz.utc))

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
        """test method nb_not_smoked_cig"""
        self.assertEqual(self.stats.nb_not_smoked_cig, 891)

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
             datetime.date(2019, 11, 25),
             datetime.date(2019, 11, 27),
             datetime.date(2019, 11, 28)]
             )

    def test_money_smoked_per_day(self):
        """test method money_smoked_per_day"""
        self.assertEqual(round(self.stats.money_smoked_per_day("2019-09-28"), 2), Decimal('5.66'))

    def test_total_money_smoked(self):
        self.assertEqual(self.stats.total_money_smoked, Decimal('159.155'))

    def test_average_money_per_day(self):
        """test method average_money_per_day"""
        self.assertEqual(round(self.stats.average_money_per_day, 2),  Decimal('2.61'))

    def test_total_money_with_starting_nb_cig(self):
        """test method total_money_with_starting_nb_cig"""
        self.assertEqual(round(self.stats.total_money_with_starting_nb_cig, 2), Decimal('591.70'))

    def test_money_saved(self):
        """test method money_saved"""
        self.assertEqual(self.stats.money_saved, Decimal('432.54'))


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
        self.stats = SmokeStats(self.user, make_aware(datetime.datetime(2020, 6, 20, 12, 0), pytz.utc), -120)

    def test_get_nb_per_day_smoke(self):
        """test method get_nb_per_day_smoke"""
        self.assertEqual(self.stats.nb_per_day(datetime.date(2020, 6, 19)), 17)
        self.assertEqual(self.stats.nb_per_day(datetime.date(2020, 6, 20)), 16)

    def test_money_smoked_per_day(self):
        """test method money_smoked_per_day"""
        self.assertEqual(self.stats.money_smoked_per_day("2020-06-19"), Decimal('8.24'))
        self.assertEqual(self.stats.money_smoked_per_day("2020-06-20"),  Decimal('7.76'))

    def test_total_cig_with_old_habits(self):
        """test method total_cig_with_old_habits"""
        self.assertEqual(self.stats.total_cig_with_old_habits, 20)

    def test_nb_not_smoked_cig_full_days(self):
        """test method nb_not_smoked_cig"""
        self.assertEqual(self.stats.nb_not_smoked_cig, 3)

    def test_average_money_per_day(self):
        """test method average_money_per_day"""
        self.assertEqual(self.stats.average_money_per_day, Decimal('8.245'))

    def test_list_dates(self):
        """test method list_dates"""
        self.assertEqual(len(self.stats.list_dates), 2)
        self.assertEqual(
            self.stats.list_dates,
            [datetime.date(2020, 6, 19), datetime.date(2020, 6, 20)]
            )

    def test_total_money_smoked(self):
        """test method total_money_smoked"""
        self.assertEqual(self.stats.total_money_smoked, Decimal('8.245'))

    def test_total_money_with_starting_nb_cig(self):
        """test method total_money_with_starting_nb_cig"""
        self.assertEqual(self.stats.total_money_with_starting_nb_cig, Decimal('9.7'))

    def test_money_saved(self):
        """test method money_saved"""
        self.assertEqual(self.stats.money_saved, Decimal('1.46'))


class StatsFirstDay(TestCase):
    """class testing Stats while first day """

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
        ConsoCig.objects.filter(user=self.user, datetime_cig__gt=datetime.datetime(2020, 6, 19, 22, 0, tzinfo=pytz.utc)).delete()
        self.stats = SmokeStats(self.user, make_aware(datetime.datetime(2020, 6, 19, 23, 59), pytz.utc), -120)

    def test_first_day(self):
        """test first day user use app"""
        self.assertTrue(self.stats.first_day)

    def test_total_smoke_all_days(self):
        """test method total_smoke_all_days for first day user"""
        self.assertEqual(self.stats.total_smoke_all_days, 17)

    def test_average_per_day(self):
        """test method average_per_day for first day user"""
        self.assertEqual(self.stats.average_per_day, 17)

    def test_count_no_smoking_day(self):
        """test method count_no_smoking_day for first day user"""
        self.assertEqual(self.stats.count_no_smoking_day, 0)

    def test_total_cig_with_old_habits(self):
        """test method total_cig_with_old_habits for first day user"""
        self.assertEqual(self.stats.total_cig_with_old_habits, 20)

    def test_nb_not_smoked_cig_full_days(self):
        """test method nb_not_smoked_cig for first day user"""
        self.assertEqual(self.stats.nb_not_smoked_cig, 3)

    def test_total_money_smoked(self):
        """test method total_money_smoked for first day user"""
        self.assertEqual(self.stats.total_money_smoked, Decimal('8.245'))

    def test_average_money_per_day(self):
        """test method average_money_per_day for first day user"""
        self.assertEqual(self.stats.average_money_per_day, self.stats.total_money_smoked)

    def test_total_money_with_starting_nb_cig(self):
        """test method money_with_starting_nb_cig for first day user"""
        self.assertEqual(self.stats.total_money_with_starting_nb_cig,  Decimal('9.700'))

    def test_money_saved(self):
        """test method money_saved for first day user"""
        self.assertEqual(self.stats.money_saved, Decimal('1.46'))

    def test_average_alternative_first_day(self):
        """test method average_alternative for first day user"""
        alternatives = CreateAlternative(self.user, row_alternative_data)
        alternatives.populate_db()
        ConsoAlternative.objects.create(
            user=self.user,
            datetime_alter=datetime.datetime(2020, 6, 19, 11, 55, tzinfo=pytz.utc),
            alternative=Alternative.objects.get(id=1001),
            activity_duration=40
            )
        ConsoAlternative.objects.create(
            user=self.user,
            datetime_alter=datetime.datetime(2020, 6, 19, 13, 30, tzinfo=pytz.utc),
            alternative=Alternative.objects.get(id=1004),
            )
        stats = HealthyStats(self.user, make_aware(datetime.datetime(2020, 6, 19, 23, 59), pytz.utc), -120)
        self.assertTrue(stats.first_day)


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
        self.stats = HealthyStats(self.user, make_aware(datetime.datetime(2019, 11, 28, 23, 59), pytz.utc), -120)

    def test_update_models_dt_user(self):
        """test method updating field dt_user in db wwith actual tz_offset"""
        conso = ConsoAlternative.objects.get(user=self.user, datetime_alter=datetime.datetime(2019, 9, 28, 20, 20, tzinfo=pytz.utc))
        self.assertEqual(conso.user_dt, datetime.datetime(2019, 9, 28, 22, 20, tzinfo=pytz.utc))

    def test_filter_queryset_for_report(self):
        """test method filter_queryset_for_report"""
        self.assertEqual(self.stats.filter_queryset_for_report().count(), 34)
        self.assertEqual(self.stats.filter_queryset_for_report(type_alt='Sp').count(), 16)
        self.assertEqual(self.stats.filter_queryset_for_report('Su').count(), 24)
        self.assertEqual(self.stats.filter_queryset_for_report('Su', type_alt='P').count(), 9)

    def test_report_substitut_per_period(self):
        """test method report_alternative_per_period """
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19)), 155)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), type_alt='Lo'), 125)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), period='week'), 215)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), period='week', type_alt='Sp'), 60)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), period='month'), 808)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), period='month', type_alt='Sp'), 413)

        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), 'Su'), 2)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), 'Su', type_alt='PAST'), 1)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), 'Su', period='week'), 3)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), 'Su', period='week', type_alt='PAST'), 2)
        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), 'Su', period='month', type_alt='PAST'), 10)

        self.assertEqual(self.stats.report_alternative_per_period(datetime.date(2019, 10, 19), 'Adfqsfc', period='weekdgfa', type_alt='Pdsf'), None)

    def test_filter_by_period(self):
        """test method filter_by_period"""
        self.assertEqual(self.stats.filter_by_period(datetime.date(2019, 10, 11), 'day', self.stats.user_activities).count(), 2)
        self.assertEqual(self.stats.filter_by_period(datetime.date(2019, 10, 11), 'week', self.stats.user_activities).count(), 6)
        self.assertEqual(self.stats.filter_by_period(datetime.date(2019, 10, 11), 'month', self.stats.user_activities).count(), 21)

    def test_convert_minutes_to_hours_min_str(self):
        """test method convert_minutes_to_hours_min_str"""
        self.assertEqual(self.stats.convert_minutes_to_hours_min_str('dfgqefg'), None)
        self.assertEqual(self.stats.convert_minutes_to_hours_min_str(), None)
        self.assertEqual(self.stats.convert_minutes_to_hours_min_str(25),'25 minutes')
        self.assertEqual(self.stats.convert_minutes_to_hours_min_str(384),'6h24')

    def test_nicotine_per_day(self):
        """test method nicotine_per_day"""
        self.assertEqual(self.stats.nicotine_per_day(datetime.date(2019, 10, 19)), 9)
