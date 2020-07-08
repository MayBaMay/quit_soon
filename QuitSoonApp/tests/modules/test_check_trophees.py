#!/usr/bin/env python

"""Module testing health user action manager module"""

import datetime
from datetime import datetime as dt
from datetime import date
import calendar
import pandas as pd
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from QuitSoonApp.modules import Trophee_checking
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Trophee
    )
from QuitSoonApp.modules import SmokeStats

from QuitSoonApp.tests.MOCK_DATA import (
    Create_packs, Create_smoke,
    row_paquet_data, fake_smoke_for_trophees, fake_smoke
    )

# user = User.objects.get(username='maykimay')
# stats = SmokeStats(user, datetime.date(2020, 7, 20))

class CheckTropheeTestCase(TestCase):
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
        self.smoke = Create_smoke(self.user, fake_smoke_for_trophees)
        self.smoke.populate_db()
        stats = SmokeStats(self.user, datetime.date(2020, 12, 31))
        self.check_trophee = Trophee_checking(stats)

    def test_values_per_dates(self):
        """
        test method values_per_dates
        get count cig smoked (col nb_cig) per dates(index) in DataFrame
        """
        df = self.check_trophee.values_per_dates
        self.assertEqual(df.columns.values.tolist(), ['nb_cig'])
        self.assertEqual(df.shape, (7, 1))
        self.assertEqual(df.loc['2020-06-19', 'nb_cig'], 19)
        self.assertEqual(df.loc['2020-06-20', 'nb_cig'], 14)
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
        df = self.check_trophee.all_dates
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
        all_days_df = self.check_trophee.all_dates
        nb_cig_per_date_df = self.check_trophee.values_per_dates
        df = self.check_trophee.smoking_values_per_dates_with_all_dates_df(all_days_df, nb_cig_per_date_df)

        self.assertEqual(df.columns.values.tolist(), ['date', 'nb_cig'])
        sum_days = 12+31+31+30+31+30+30
        self.assertEqual(df.shape, (sum_days, 2))
        self.assertEqual(df[(df['date'] == '2020-06-19')].nb_cig.values, [19.0])
        self.assertEqual(df[(df['date'] == '2020-06-20')].nb_cig.values, [14.0])
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
        s = self.check_trophee.get_conso_occurence(10)
        # from 2020-06-21 to 2020-12-31 = occurence less then 10 cigarettes smoke
        self.assertTrue(193.0 in s.values)
        # sum occurence in s = sum less than 10 cig a month
        self.assertEqual(s.sum(), 193)


    def test_get_nans_occurence(self):
        """
        test method get_nans_occurence
        get NaNs occurence in dataframe
        """
        s = self.check_trophee.get_nans_occurence()
        print(s)
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
        get trophees user didn't completed yet in a list
        """
        # trophee checking never done
        trophees = self.check_trophee.list_user_challenges
        self.assertEqual(trophees, [
            (15, 3), (15, 7), (10, 3), (10, 7), (5, 3), (5, 7),
            (4, 3), (4, 7), (3, 3), (3, 7), (2, 3), (2, 7), (1, 3), (1, 7),
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 10), (0, 15),
            (0, 20), (0, 25), (0, 30), (0, 60), (0, 90),
            (0, 120), (0, 150), (0, 180), (0, 210), (0, 240),
            (0, 270), (0, 300) , (0, 330)])
        #trophee checking already done ones and Trophees exits in Trophee table
        Trophee.objects.create(user=self.user, nb_cig=0, nb_jour=1)
        Trophee.objects.create(user=self.user, nb_cig=15, nb_jour=3)
        trophees = self.check_trophee.list_user_challenges
        self.assertEqual(trophees, [
            (15, 7), (10, 3), (10, 7), (5, 3), (5, 7), (4, 3), (4, 7),
            (3, 3), (3, 7), (2, 3), (2, 7), (1, 3), (1, 7), (0, 2),
            (0, 3), (0, 4), (0, 7), (0, 10), (0, 15), (0, 20), (0, 25),
            (0, 30), (0, 60), (0, 90), (0, 120), (0, 150), (0, 180),
            (0, 210), (0, 240),(0, 270), (0, 300) , (0, 330)])

    def test_check_days_trophees(self):
        """
        test method check_days_trophees
        for element in occurence, check if >= element in trophee to succeed list
        return list of trophees to create
        """
        ConsoCig.objects.filter(user=self.user, date_cig__gte='2020-07-5').delete()
        stats = SmokeStats(self.user, datetime.date(2020, 6, 26))
        check_trophee = Trophee_checking(stats)
        self.assertTrue(check_trophee.check_days_trophees(challenge=(15, 3)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(15, 7)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(10, 3)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(10, 7)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(5, 3)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(5, 7)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(4, 3)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(4, 7)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(3, 3)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(3, 7)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(2, 3)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(2, 7)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(1, 3)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(1, 7)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(0, 1)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(0, 2)))
        self.assertTrue(check_trophee.check_days_trophees(challenge=(0, 3)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(0, 4)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(0, 7)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(0, 10)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(0, 15)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(0, 20)))
        self.assertFalse(check_trophee.check_days_trophees(challenge=(0, 25)))


    def test_parse_smoking_month(self):
        """
        test method parse_smoking_month
        for each month check if full and not smoking (True), else False
        """
        month_parsed = self.check_trophee.parse_smoking_month
        self.assertEqual(month_parsed, [False, False, True, True, False, True, False])

    def test_check_month_trophees(self):
        """
        test method check_month_trophees
        check if completed trophees months without smoking
        """
        self.assertTrue(self.check_trophee.check_month_trophees(30))
        self.assertTrue(self.check_trophee.check_month_trophees(60))
        self.assertFalse(self.check_trophee.check_month_trophees(90))
        self.assertFalse(self.check_trophee.check_month_trophees(120))
        self.assertFalse(self.check_trophee.check_month_trophees(150))
        self.assertFalse(self.check_trophee.check_month_trophees(180))
        self.assertFalse(self.check_trophee.check_month_trophees(210))
        self.assertFalse(self.check_trophee.check_month_trophees(240))
        self.assertFalse(self.check_trophee.check_month_trophees(270))
        self.assertFalse(self.check_trophee.check_month_trophees(300))
        self.assertFalse(self.check_trophee.check_month_trophees(330))

    def test_trophees_accomplished(self):
        self.check_trophee.trophees_accomplished
        self.assertEqual(
            self.check_trophee.user_trophees,
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
        Trophee.objects.filter(user=self.user).delete()
        ConsoCig.objects.filter(user=self.user, date_cig__gte='2020-07-5').delete()
        stats = SmokeStats(self.user, datetime.date(2020, 6, 26))
        check_trophee = Trophee_checking(stats)
        check_trophee.trophees_accomplished
        self.assertEqual(
            check_trophee.user_trophees,
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
        ConsoCig.objects.filter(user=self.user).delete()
        Trophee.objects.filter(user=self.user).delete()
        stats = SmokeStats(self.user, datetime.date(2020, 6, 19))
        check_trophee = Trophee_checking(stats)
        check_trophee.trophees_accomplished
        self.assertEqual(
            check_trophee.user_trophees,
            {(15, 3): False, (15, 7): False, (10, 3): False, (10, 7): False,
            (5, 3): False, (5, 7): False, (4, 3): False, (4, 7): False,
            (3, 3): False, (3, 7): False, (2, 3): False, (2, 7): False, (1, 3): False,
            (1, 7): False, (0, 1): False, (0, 2): False, (0, 3): False, (0, 4): False,
            (0, 7): False, (0, 10): False, (0, 15): False, (0, 20): False,
            (0, 25): False, (0, 30): False, (0, 60): False, (0, 90): False,
            (0, 120): False, (0, 150): False, (0, 180): False, (0, 210): False,
            (0, 240): False, (0, 270): False, (0, 300): False, (0, 330): False}
            )

    def test_create_trophees_no_smoking(self):
        """
        test method create_trophees_no_smoking
        With list trophees to create, create trophees in database
        """
        self.check_trophee.create_trophees()
        trophees = Trophee.objects.filter(user=self.user)
        self.assertTrue(trophees.exists())
        self.assertTrue(trophees.count(), len(self.check_trophee.trophees_accomplished))
        self.assertTrue(trophees.get(nb_cig=0, nb_jour=1))
        self.assertTrue(trophees.get(nb_cig=15, nb_jour=3))
        self.assertEqual(trophees.count(), 25)
