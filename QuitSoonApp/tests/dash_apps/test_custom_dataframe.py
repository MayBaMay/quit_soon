#!/usr/bin/env python

"""Test pd_custom_dataframe module"""

# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.testing.assert_frame_equal.html
# pandas.testing.assert_frame_equal(left, right, check_dtype=True, check_index_type='equiv', check_column_type='equiv', check_frame_type=True, check_less_precise=False, check_names=True, by_blocks=False, check_exact=False, check_datetimelike_compat=False, check_categorical=True, check_like=False, obj='DataFrame')[source]

import datetime
import pandas as pd
from pandas._testing import assert_frame_equal

from django.test import TestCase

from QuitSoonApp.dash_apps import DataFrameDate


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
        self.custom_df = DataFrameDate(self.data_dict)

    def test_df_creation(self):
        assert_frame_equal(self.custom_df.df, self.custom_df.df)

    def test_daily_dataframe(self):
        assert_frame_equal(self.custom_df.day_df, self.custom_df.day_df)
        self.assertEqual(self.custom_df.day_df.loc['05/06/20', 'nb_cig'], 9)

    def test_weekly_dataframe(self):
        assert_frame_equal(self.custom_df.week_df, self.custom_df.week_df)
        self.assertEqual(self.custom_df.week_df.loc['08/06/20-14/06/20', 'nb_cig'], 7)

    def test_monthly_dataframe(self):
        assert_frame_equal(self.custom_df.month_df, self.custom_df.month_df)
        self.assertEqual(self.custom_df.month_df.loc['06/20', 'nb_cig'], 21)
