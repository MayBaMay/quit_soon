from datetime import datetime as dt
from datetime import timedelta
import json

import pandas as pd


class DataFrameDate:

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def init_frame(self):
        # create row DataFrame with data
        return pd.DataFrame(self.data_dict, columns=['date', 'nb_cig', 'money_smoked', 'activity_duration']).set_index('date')

    @property
    def day_df(self):
        # create day DataFrame
        df = self.init_frame()
        # group by day
        day_df = df.groupby(pd.Grouper(freq='D')).sum()
        day_df.index = day_df.index.strftime("%d/%m/%y")
        return day_df

    @property
    def week_df(self):
        # create week DataFrame
        df = self.init_frame()
        # group by week
        week_df = df.groupby(pd.Grouper(freq='W')).sum()
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
        # create month DataFrame
        df = self.init_frame()
        month_df = df.groupby(pd.Grouper(freq='M')).sum()
        month_df.index = month_df.index.strftime("%m/%y")
        return month_df

    @property
    def year_df(self):
        # create year DataFrame
        df = self.init_frame()
        year_df = df.groupby(pd.Grouper(freq='Y')).sum()
        year_df.index = year_df.index.strftime("%Y")
        return year_df


if __name__ == '__main__':
    with open('user_dict.txt') as json_file:
        user_dict = json.load(json_file)
        i=0
        for p in user_dict['date']:
            user_dict['date'][i] = dt.strptime(p, '%Y-%m-%d')
            i += 1
        i=0
        for p in user_dict['money_smoked']:
            user_dict['money_smoked'][i] = float(user_dict['money_smoked'][i])
            i += 1
    df = DataFrameDate(user_dict)
    print(df.init_frame().money_smoked)
    print('day', df.day_df)
    print('week', df.week_df)
    print('month', df.month_df)
    print('year', df.year_df)
