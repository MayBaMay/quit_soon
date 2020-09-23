#!/usr/bin/env python

"""Module testing health user action manager module"""

import datetime
from datetime import datetime as dt
from datetime import date
import pytz
import calendar
import pandas as pd
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.utils.timezone import make_aware

from QuitSoonApp.modules import TrophyManager
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Trophy
    )
from QuitSoonApp.modules import SmokeStats

from QuitSoonApp.tests.MOCK_DATA import (
    BaseTestCase, 
    Create_packs, Create_smoke,
    row_paquet_data, fake_smoke_for_trophies, fake_smoke
    )


class ChecktrophyTestCase(BaseTestCase):
    """class testing Create_smoke """

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.profile = UserProfile.objects.create(
            user=self.usertest,
            date_start="2020-06-19",
            starting_nb_cig=20
            )
        self.packs = Create_packs(self.usertest, row_paquet_data)
        self.packs.populate_db()
        self.smoke = Create_smoke(self.usertest, fake_smoke_for_trophies)
        self.smoke.populate_db()
        stats = SmokeStats(self.usertest, make_aware(datetime.datetime(2020, 12, 31, 12, 0), pytz.utc), -120)
        self.check_trophy = TrophyManager(stats)

    def test_values_per_dates(self):
        """
        test method values_per_dates
        get count cig smoked (col nb_cig) per dates(index) in DataFrame
        """
        df = self.check_trophy.values_per_dates
        self.assertEqual(df.columns.values.tolist(), ['nb_cig'])
        self.assertEqual(df.shape, (7, 1))
        self.assertEqual(df.loc['2020-06-19', 'nb_cig'], 17)
        self.assertEqual(df.loc['2020-06-20', 'nb_cig'], 16)
        self.assertEqual(df.loc['2020-06-22', 'nb_cig'], 1)
        self.assertEqual(df.loc['2020-06-26', 'nb_cig'], 1)
        self.assertEqual(df.loc['2020-07-05', 'nb_cig'], 1)
        self.assertEqual(df.loc['2020-07-19', 'nb_cig'], 1)
        self.assertEqual(df.loc['2020-10-19', 'nb_cig'], 1)
        # current day not in df
        with self.assertRaises(KeyError) as raises:
            df.loc['2020-12-31', 'nb_cig']

    def test_all_dates(self):
        """
        test method all_dates
        get all passed dates, index of empty dataframe
        """
        df = self.check_trophy.all_dates
        self.assertEqual(df.columns.values.tolist(), [])
        sum_days = 12+31+31+30+31+30+30
        self.assertEqual(df.shape, (sum_days, 0))
        self.assertEqual(df.index[0], dt(2020, 6, 19))
        self.assertEqual(df.index[1], dt(2020, 6, 20))
        self.assertEqual(df.index[2], dt(2020, 6, 21))
        self.assertEqual(df.index[7], dt(2020, 6, 26))
        self.assertEqual(df.index[16], dt(2020, 7, 5))
        self.assertEqual(df.index[30], dt(2020, 7, 19))
        # current day not in df
        self.assertEqual(df.index[-1], dt(2020, 12, 30))
        self.assertEqual(df.columns.values.tolist(), [])

    def test_smoking_values_per_dates_with_all_dates_df(self):
        """
        test method smoking_values_per_dates_with_all_dates_df
        get dataframe with all passed dates(index) and count cig per dates (col nb_cig)
        """
        all_days_df = self.check_trophy.all_dates
        nb_cig_per_date_df = self.check_trophy.values_per_dates
        df = self.check_trophy.smoking_values_per_dates_with_all_dates_df(all_days_df, nb_cig_per_date_df)

        self.assertEqual(df.columns.values.tolist(), ['date', 'nb_cig'])
        sum_days = 12+31+31+30+31+30+30
        self.assertEqual(df.shape, (sum_days, 2))
        self.assertEqual(df[(df['date'] == '2020-06-19')].nb_cig.values, [17.0])
        self.assertEqual(df[(df['date'] == '2020-06-20')].nb_cig.values, [16.0])
        self.assertEqual(df[(df['date'] == '2020-06-22')].nb_cig.values, [1.0])
        self.assertEqual(df[(df['date'] == '2020-06-26')].nb_cig.values, [1.0])
        self.assertEqual(df[(df['date'] == '2020-07-05')].nb_cig.values, [1.0])
        self.assertEqual(df[(df['date'] == '2020-07-19')].nb_cig.values, [1.0])
        self.assertEqual(df[(df['date'] == '2020-10-19')].nb_cig.values, [1.0])
        # nb_cig col = NaN if no smoke
        self.assertTrue(pd.isna(df[(df['date'] == '2020-07-01')].nb_cig.values))
        self.assertTrue(pd.isna(df[(df['date'] == '2020-07-06')].nb_cig.values))
        self.assertTrue(pd.isna(df[(df['date'] == '2020-07-18')].nb_cig.values))
        # only 2 days smoke so NaNs nb_cig = count rows - days smoke
        self.assertEqual(pd.isna(df.nb_cig).sum(), sum_days-7)

    def test_get_conso_occurence(self):
        s = self.check_trophy.get_conso_occurence(10)
        # from 2020-06-21 to 2020-12-31 = occurence less then 10 cigarettes smoke
        self.assertTrue(193.0 in s.values)
        # sum occurence in s = sum less than 10 cig a month
        self.assertEqual(s.sum(), 193)

    def test_get_nans_occurence(self):
        """
        test method get_nans_occurence
        get NaNs occurence in dataframe
        """
        s = self.check_trophy.get_nans_occurence()
        # 2020-06-21 = 1 days non smoke
        self.assertTrue(1.0 in s.values)
        # from 2020-06-23 to 2020-06-25 = 3 days non smoke
        self.assertTrue(3.0 in s.values)
        # from 2020-06-27 to 2020-07-04 = 8 days non smoke
        self.assertTrue(8.0 in s.values)
        # from 2020-07-06 to 2020-07-18 = 13 days non smoke
        self.assertTrue(13.0 in s.values)
        # from 2020-07-20 to 2020-10-18
        self.assertTrue(91.0 in s.values)
        # from 2020-10-19 to 2020-12-30
        self.assertTrue(72.0 in s.values)
        # sum occurence in s = sum non smoking days
        self.assertEqual(s.sum(), 1+3+8+13+91+72)

    def test_list_user_challenges(self):
        """
        test method list_user_challenges
        get trophies user didn't completed yet in a list
        """
        # trophy checking never done
        trophies = self.check_trophy.list_user_challenges
        self.assertEqual(trophies, [
            (15, 3), (15, 7), (10, 3), (10, 7), (5, 3), (5, 7),
            (4, 3), (4, 7), (3, 3), (3, 7), (2, 3), (2, 7), (1, 3), (1, 7),
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 10), (0, 15),
            (0, 20), (0, 25), (0, 30), (0, 60), (0, 90),
            (0, 120), (0, 150), (0, 180), (0, 210), (0, 240),
            (0, 270), (0, 300) , (0, 330)])
        #trophy checking already done ones and trophies exits in trophy table
        Trophy.objects.create(user=self.usertest, nb_cig=0, nb_jour=1)
        Trophy.objects.create(user=self.usertest, nb_cig=15, nb_jour=3)
        trophies = self.check_trophy.list_user_challenges
        self.assertEqual(trophies, [
            (15, 7), (10, 3), (10, 7), (5, 3), (5, 7), (4, 3), (4, 7),
            (3, 3), (3, 7), (2, 3), (2, 7), (1, 3), (1, 7), (0, 2),
            (0, 3), (0, 4), (0, 7), (0, 10), (0, 15), (0, 20), (0, 25),
            (0, 30), (0, 60), (0, 90), (0, 120), (0, 150), (0, 180),
            (0, 210), (0, 240),(0, 270), (0, 300) , (0, 330)])

    def test_check_days_trophies(self):
        """
        test method check_days_trophies
        for element in occurence, check if >= element in trophy to succeed list
        return list of trophies to create
        """
        ConsoCig.objects.filter(user=self.usertest, datetime_cig__gte=dt(2020, 7, 5, 23, 59, tzinfo=pytz.utc)).delete()
        stats = SmokeStats(self.usertest, make_aware(dt(2020, 6, 26, 12, 0), pytz.utc), -120)
        check_trophy = TrophyManager(stats)
        self.assertTrue(check_trophy.check_days_trophies(challenge=(15, 3)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(15, 7)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(10, 3)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(10, 7)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(5, 3)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(5, 7)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(4, 3)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(4, 7)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(3, 3)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(3, 7)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(2, 3)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(2, 7)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(1, 3)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(1, 7)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(0, 1)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(0, 2)))
        self.assertTrue(check_trophy.check_days_trophies(challenge=(0, 3)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(0, 4)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(0, 7)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(0, 10)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(0, 15)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(0, 20)))
        self.assertFalse(check_trophy.check_days_trophies(challenge=(0, 25)))

    def test_parse_smoking_month(self):
        """
        test method parse_smoking_month
        for each month check if full and not smoking (True), else False
        """
        month_parsed = self.check_trophy.parse_smoking_month
        self.assertEqual(month_parsed, [False, False, True, True, False, True, False])

    def test_check_month_trophies(self):
        """
        test method check_month_trophies
        check if completed trophies months without smoking
        """
        self.assertTrue(self.check_trophy.check_month_trophies(30))
        self.assertTrue(self.check_trophy.check_month_trophies(60))
        self.assertFalse(self.check_trophy.check_month_trophies(90))
        self.assertFalse(self.check_trophy.check_month_trophies(120))
        self.assertFalse(self.check_trophy.check_month_trophies(150))
        self.assertFalse(self.check_trophy.check_month_trophies(180))
        self.assertFalse(self.check_trophy.check_month_trophies(210))
        self.assertFalse(self.check_trophy.check_month_trophies(240))
        self.assertFalse(self.check_trophy.check_month_trophies(270))
        self.assertFalse(self.check_trophy.check_month_trophies(300))
        self.assertFalse(self.check_trophy.check_month_trophies(330))

    def test_trophies_accomplished(self):
        self.check_trophy.trophies_accomplished
        self.assertEqual(
            self.check_trophy.user_trophies,
            {(15, 3): True, (15, 7): True, (10, 3): True, (10, 7): True,
            (5, 3): True, (5, 7): True, (4, 3): True, (4, 7): True,
            (3, 3): True, (3, 7): True, (2, 3): True, (2, 7): True, (1, 3): True,
            (1, 7): True, (0, 1): True, (0, 2): True, (0, 3): True, (0, 4): True,
            (0, 7): True, (0, 10): True, (0, 15): True, (0, 20): True,
            (0, 25): True, (0, 30): True, (0, 60): True, (0, 90): False,
            (0, 120): False, (0, 150): False, (0, 180): False, (0, 210): False,
            (0, 240): False, (0, 270): False, (0, 300): False, (0, 330): False}
            )
        # test with less days non smoked
        Trophy.objects.filter(user=self.usertest).delete()
        ConsoCig.objects.filter(user=self.usertest, datetime_cig__gte=dt(2020, 7, 5, 23, 59, tzinfo=pytz.utc)).delete()
        stats = SmokeStats(self.usertest, make_aware(dt(2020, 6, 26, 12, 0), pytz.utc), -120)

        check_trophy = TrophyManager(stats)
        check_trophy.trophies_accomplished
        self.assertEqual(
            check_trophy.user_trophies,
            {(15, 3): True, (15, 7): False, (10, 3): True, (10, 7): False,
            (5, 3): True, (5, 7): False, (4, 3): True, (4, 7): False,
            (3, 3): True, (3, 7): False, (2, 3): True, (2, 7): False, (1, 3): True,
            (1, 7): False, (0, 1): True, (0, 2): True, (0, 3): True, (0, 4): False,
            (0, 7): False, (0, 10): False, (0, 15): False, (0, 20): False,
            (0, 25): False, (0, 30): False, (0, 60): False, (0, 90): False,
            (0, 120): False, (0, 150): False, (0, 180): False, (0, 210): False,
            (0, 240): False, (0, 270): False, (0, 300): False, (0, 330): False}
            )
        # test first day
        ConsoCig.objects.filter(user=self.usertest).delete()
        Trophy.objects.filter(user=self.usertest).delete()
        stats = SmokeStats(self.usertest, make_aware(datetime.datetime(2020, 6, 19, 12, 0), pytz.utc), -120)
        check_trophy = TrophyManager(stats)
        check_trophy.trophies_accomplished
        self.assertEqual(
            check_trophy.user_trophies,
            {(15, 3): False, (15, 7): False, (10, 3): False, (10, 7): False,
            (5, 3): False, (5, 7): False, (4, 3): False, (4, 7): False,
            (3, 3): False, (3, 7): False, (2, 3): False, (2, 7): False, (1, 3): False,
            (1, 7): False, (0, 1): False, (0, 2): False, (0, 3): False, (0, 4): False,
            (0, 7): False, (0, 10): False, (0, 15): False, (0, 20): False,
            (0, 25): False, (0, 30): False, (0, 60): False, (0, 90): False,
            (0, 120): False, (0, 150): False, (0, 180): False, (0, 210): False,
            (0, 240): False, (0, 270): False, (0, 300): False, (0, 330): False}
            )

    def test_create_trophies_no_smoking(self):
        """
        test method create_trophies_no_smoking
        With list trophies to create, create trophies in database
        """
        self.check_trophy.create_trophies()
        trophies = Trophy.objects.filter(user=self.usertest)
        self.assertTrue(trophies.exists())
        self.assertTrue(trophies.count(), len(self.check_trophy.trophies_accomplished))
        self.assertTrue(trophies.get(nb_cig=0, nb_jour=1))
        self.assertTrue(trophies.get(nb_cig=15, nb_jour=3))
        self.assertEqual(trophies.count(), 25)
        self.assertEqual(
            self.check_trophy.user_trophies,
            {(15, 3): True, (15, 7): True, (10, 3): True, (10, 7): True,
            (5, 3): True, (5, 7): True, (4, 3): True, (4, 7): True,
            (3, 3): True, (3, 7): True, (2, 3): True, (2, 7): True, (1, 3): True,
            (1, 7): True, (0, 1): True, (0, 2): True, (0, 3): True, (0, 4): True,
            (0, 7): True, (0, 10): True, (0, 15): True, (0, 20): True,
            (0, 25): True, (0, 30): True, (0, 60): True, (0, 90): False,
            (0, 120): False, (0, 150): False, (0, 180): False, (0, 210): False,
            (0, 240): False, (0, 270): False, (0, 300): False, (0, 330): False}
            )
