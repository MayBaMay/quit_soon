#!/usr/bin/env python
"""Make dictionnary into panda dataframe with period treatment properties """

from datetime import datetime as dt
from datetime import timedelta, date
import json

import pandas as pd

from QuitSoonApp.models import UserProfile


class DataFrameDate:
    """
    Class object initiating a dataframe with date as index
    and giving property periods of this dataframe
    """

    def __init__(self, data_dict, user):
        self.data_dict = data_dict
        self.user = user
        self.df = self.user_data_df

    @property
    def user_data_df(self):
        """create a dataframe with all user data including unused dates"""
        all_data = pd.DataFrame(self.data_dict, columns=['date', 'nb_cig', 'money_smoked', 'activity_duration']).set_index('date')
        return self.concat_df_with_all_dates(all_data, self.all_user_dates_in_df)

    @staticmethod
    def daterange(start_date, end_date):
        """generate all dates from start_date to end_date """
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    @property
    def all_user_dates_in_df(self):
        """create a dataframe with dates since user start app"""
        start_date = UserProfile.objects.get(user=self.user).date_start
        end_date = date.today()
        dates = []
        for single_date in self.daterange(start_date, end_date):
            dates.append({'date':pd.to_datetime(single_date)})
        return pd.DataFrame(dates, columns=['date']).set_index('date')

    def concat_df_with_all_dates(self, user_data, all_dates):
        """concat user data df with all_dates df"""
        return pd.concat([user_data, all_dates], axis=1).rename(columns={"date_cig":"nb_cig"})

    @property
    def day_df(self):
        """dataframe in a dayly bases"""
        day_df = self.df.groupby(pd.Grouper(freq='D')).sum()
        day_df.index = day_df.index.strftime("%d/%m/%y")
        return day_df

    @property
    def week_df(self):
        """dataframe in a weekly bases"""
        week_df = self.df.groupby(pd.Grouper(freq='W')).sum()
        # format index
        for date in week_df.index:
            start = date - timedelta(days=date.weekday())
            end = start + timedelta(days=6)
            as_list = week_df.index.tolist()
            idx = as_list.index(date)
            as_list[idx] = "{}-{}".format(start.strftime('%d/%m/%y'), end.strftime('%d/%m/%y'))
            week_df.index = as_list
        return week_df

    @property
    def month_df(self):
        """dataframe in a monthly bases"""
        month_df = self.df.groupby(pd.Grouper(freq='M')).sum()
        month_df.index = month_df.index.strftime("%m/%y")
        return month_df
