#!/usr/bin/env python
"""Make dictionnary into panda dataframe with period treatment properties """

from datetime import timedelta

import pandas as pd


class DataFrameDate:
    """
    Class object initiating a dataframe with date as index
    and giving property periods of this dataframe
    """

    def __init__(self, data_dict, focus):
        self.df_chartdata = pd.DataFrame(
            data_dict,
            columns=['date', focus, 'activity_duration']
            ).set_index('date')

    @property
    def day_df(self):
        """dataframe in a dayly bases"""
        day_df = self.df_chartdata.groupby(pd.Grouper(freq='D')).sum()
        day_df.index = day_df.index.strftime("%d/%m/%y")
        return day_df

    @property
    def week_df(self):
        """dataframe in a weekly bases"""
        week_df = self.df_chartdata.groupby(pd.Grouper(freq='W')).sum().round(2)
        # format index
        for date in week_df.index:
            start = date - timedelta(days=date.weekday())
            end = start + timedelta(days=6)
            formated_date = week_df.index.tolist()
            idx = formated_date.index(date)
            formated_date[idx] = "{}-{}".format(start.strftime('%d/%m'), end.strftime('%d/%m'))
            week_df.index = formated_date
        return week_df

    @property
    def month_df(self):
        """dataframe in a monthly bases"""
        month_df = self.df_chartdata.groupby(pd.Grouper(freq='M')).sum().round(2)
        month_df.index = month_df.index.strftime("%m/%y")
        return month_df
