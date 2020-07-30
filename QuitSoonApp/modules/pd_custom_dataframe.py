#!/usr/bin/env python
"""Make dictionnary into panda dataframe with period treatment properties """

from datetime import datetime as dt
from datetime import timedelta
import json

import pandas as pd


class DataFrameDate:
    """
    Class object initiating a dataframe with date as index
    and giving property periods of this dataframe
    """

    def __init__(self, data_dict, focus):
        if focus == 'nb_cig':
            self.df = pd.DataFrame(data_dict, columns=['date', 'nb_cig', 'activity_duration']).set_index('date')
        elif focus == 'money_smoked':
            self.df = pd.DataFrame(data_dict, columns=['date', 'money_smoked', 'activity_duration']).set_index('date')
        elif focus == 'nicotine':
            self.df = pd.DataFrame(data_dict, columns=['date', 'activity_duration', 'nicotine']).set_index('date')

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
            formated_date = week_df.index.tolist()
            idx = formated_date.index(date)
            formated_date[idx] = start.strftime('%d/%m/%y')
            week_df.index = formated_date
        return week_df

    @property
    def month_df(self):
        """dataframe in a monthly bases"""
        month_df = self.df.groupby(pd.Grouper(freq='M')).sum()
        month_df.index = month_df.index.strftime("%m/%y")
        return month_df
