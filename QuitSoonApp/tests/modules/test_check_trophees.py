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
    row_paquet_data, fake_smoke_for_trophees
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
        s = self.check_trophee.get_nans_occurence
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

    def test_check_trophees_to_be_completed(self):
        """
        test method check_trophees_to_be_completed
        get trophees user didn't completed yet in a list
        """
        # trophee checking never done
        unparsed_list = [1, 2, 3, 4, 5, 7, 10, 15, 30, 60]
        trophees = self.check_trophee.check_trophees_to_be_completed(unparsed_list)
        self.assertEqual(trophees, [1, 2, 3, 4, 5, 7, 10, 15, 30, 60])
        # trophee checking already done ones and Trophees exits in Trophee table
        Trophee.objects.create(user=self.user, nb_cig=0, nb_jour=1)
        Trophee.objects.create(user=self.user, nb_cig=0, nb_jour=2)
        trophees = self.check_trophee.check_trophees_to_be_completed(unparsed_list)
        self.assertEqual(trophees, [3, 4, 5, 7, 10, 15, 30, 60])

    def test_check_days_trophees(self):
        """
        test method check_days_trophees
        for element in occurence de NaNs, check if >= element in trophee to succeed list
        return list of trophees to create
        """
        # first checking
        trophees_to_create = self.check_trophee.check_days_trophees
        self.assertEqual(trophees_to_create, [1, 2, 3, 4, 7, 10, 15, 20, 25])

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
        trophees_to_create = self.check_trophee.check_month_trophees
        self.assertEqual(trophees_to_create, [30, 60])

    def test_trophee_to_create(self):
        """
        test attribute trophees_to_create
        get all trophees completed during checking
        """
        self.assertEqual(self.check_trophee.trophees_to_create, [1, 2, 3, 4, 7, 10, 15, 20, 25, 30, 60])

    def test_create_trophees_no_smoking(self):
        """
        test method create_trophees_no_smoking
        With list trophees to create, create trophees in database
        """
        self.check_trophee.create_trophees_no_smoking()
        trophees = Trophee.objects.filter(user=self.user, nb_cig=0)
        self.assertTrue(trophees.exists())
        self.assertTrue(trophees.count(), len(self.check_trophee.trophees_to_create))
        self.assertTrue(trophees.get(nb_jour=1))
        self.assertTrue(trophees.get(nb_jour=2))
        self.assertTrue(trophees.get(nb_jour=3))
        self.assertTrue(trophees.get(nb_jour=4))
        self.assertTrue(trophees.get(nb_jour=7))
        self.assertTrue(trophees.get(nb_jour=10))
        self.assertTrue(trophees.get(nb_jour=15))
        self.assertTrue(trophees.get(nb_jour=20))
        self.assertTrue(trophees.get(nb_jour=25))
        self.assertTrue(trophees.get(nb_jour=30))
        self.assertTrue(trophees.get(nb_jour=60))
        self.check_trophee.create_trophees_no_smoking()
        trophees = Trophee.objects.filter(user=self.user, nb_cig=0)
        self.assertTrue(trophees.get(nb_jour=1))
