#!/usr/bin/env python
# pylint: disable=duplicate-code


"""Test pd_custom_dataframe module"""

import datetime
from pandas._testing import assert_frame_equal

from django.test import TestCase

from QuitSoonApp.modules import DataFrameDate


class DataFrameDateTestCase(TestCase):
    """test DataFrameDate class"""

    def setUp(self):
        self.data_dict = {
            'date': [datetime.datetime(2020, 6, 5, 0, 0),
                     datetime.datetime(2020, 6, 6, 0, 0),
                     datetime.datetime(2020, 6, 7, 0, 0),
                     datetime.datetime(2020, 6, 8, 0, 0),
                     datetime.datetime(2020, 6, 9, 0, 0),
                     datetime.datetime(2020, 6, 10, 0, 0),
                     datetime.datetime(2020, 6, 11, 0, 0),
                     datetime.datetime(2020, 6, 12, 0, 0),
                     datetime.datetime(2020, 6, 13, 0, 0),
                     datetime.datetime(2020, 6, 14, 0, 0),
                     datetime.datetime(2020, 6, 15, 0, 0),
                     datetime.datetime(2020, 6, 16, 0, 0)],
            'nb_cig': [9, 5, 0, 0, 0, 0, 0, 4, 0, 3, 0, 0],
            'money_smoked': [3.82, 1.68, 0.0, 0.0, 0.0, 0.0, 0.0, 1.2, 0.0, 0.9, 0.0, 0.0],
            'activity_duration': [0, 0, 0, 0, 0, 60, 0, 105, 0, 290, 0, 0],
            'nicotine': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            }
        self.custom_df_nb_cig = DataFrameDate(self.data_dict, 'nb_cig')
        self.custom_df_money_smoked = DataFrameDate(self.data_dict, 'money_smoked')
        self.custom_df_nicotine = DataFrameDate(self.data_dict, 'nicotine')

    def test_df_creation(self):
        """test df creation method"""
        assert_frame_equal(self.custom_df_nb_cig.df_chartdata, self.custom_df_nb_cig.df_chartdata)

    def test_daily_dataframe(self):
        """test day_df method"""
        assert_frame_equal(self.custom_df_nb_cig.day_df, self.custom_df_nb_cig.day_df)
        self.assertEqual(self.custom_df_nb_cig.day_df.loc['05/06/20', 'nb_cig'], 9)

    def test_weekly_dataframe(self):
        """test week_df method"""
        assert_frame_equal(self.custom_df_nb_cig.week_df, self.custom_df_nb_cig.week_df)
        self.assertEqual(self.custom_df_nb_cig.week_df.loc['08/06-14/06', 'nb_cig'], 7)

    def test_monthly_dataframe(self):
        """test month_df method"""
        assert_frame_equal(self.custom_df_nb_cig.month_df, self.custom_df_nb_cig.month_df)
        self.assertEqual(self.custom_df_nb_cig.month_df.loc['06/20', 'nb_cig'], 21)
