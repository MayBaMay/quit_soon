#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)

""" Generate data for ChartData in APIView"""

import json
import datetime
import pandas as pd

from django.utils import timezone

from QuitSoonApp.models import UserProfile
from ..utils.pd_custom_dataframe import DataFrameDate
from .stats_manager import SmokeStats, HealthyStats


class ChartManager:
    """
    Generate data for ChartData in APIView
    """

    def __init__(self, user, user_options, tz_offset):
        self.user = user
        self.user_options = user_options

        self.smoke_stats = SmokeStats(
            self.user,
            timezone.now(),
            tz_offset
            )
        self.healthy_stats = HealthyStats(
            self.user,
            timezone.now(),
            tz_offset
            )

    def time_chart_data(self):
        """ generate data for  time chart"""
        nb_days = self.smoke_stats.nb_full_days_since_start
        conso_values = self.smoke_stats.stats_user_conso.values()
        data_cig = pd.DataFrame(conso_values)
        data = data_cig.user_dt.dt.hour.value_counts()
        data_dict = {}
        for hour in range(0,24):
            try:
                if nb_days:
                    data_dict[hour] = data.loc[hour] / nb_days
                else:
                    data_dict[hour] = data.loc[hour]
            except KeyError:
                data_dict[hour] = 0
        hour_serie = pd.Series(data_dict)
        result = hour_serie.to_json(orient="split")
        parsed = json.loads(result)
        parsed["data"] = {'base':parsed["data"]}
        parsed["columns"] = 'Moyenne par heure'
        return parsed

    def generate_graph_data(self):
        """ generate data for graphs other than time_chart"""
        user_dict = {'date':[],
                     'activity_duration':[],
                     'nb_cig':[],
                     'money_smoked':[],
                     'nicotine':[]}
        for date in self.smoke_stats.list_dates:
            user_dict['date'].append(
                datetime.datetime.combine(date, datetime.datetime.min.time())
                )
            if self.healthy_stats.report_alternative_per_period(date):
                user_dict['activity_duration'].append(
                    self.healthy_stats.report_alternative_per_period(date)
                    )
            else:
                user_dict['activity_duration'].append(0)
            if self.user_options['charttype'] == 'nb_cig':
                user_dict['nb_cig'].append(self.smoke_stats.nb_per_day(date))
            elif self.user_options['charttype'] == 'money_smoked':
                user_dict['money_smoked'].append(float(self.smoke_stats.money_smoked_per_day(date)))
            elif self.user_options['charttype'] == 'nicotine':
                user_dict['nicotine'].append(self.healthy_stats.nicotine_per_day(date))
        # keep only usefull keys and value in user_dict
        return {i:user_dict[i] for i in user_dict if user_dict[i]!=[]}

    def df_period_chart(self, user_dict):
        """ generate dataframe with chart data for specific self.user_options['period'] """
        df_chart = DataFrameDate(user_dict, self.user_options['charttype'])
        if self.user_options['period'] == 'Semaine':
            return df_chart.week_df
        if self.user_options['period'] == 'Mois':
            return df_chart.month_df
        return df_chart.day_df

    def resize_chart(self, df_chart):
        """resize size of chart to the last 7 days"""
        if len(df_chart.index) > 7:
            dates_range = self.user_options['dates_range']
            if int(dates_range):
                df_chart = df_chart.iloc[
                    -7 + int(dates_range): int(dates_range)
                    ]
            else:
                df_chart = df_chart.tail(7)
        return df_chart

    @property
    def get_parsed_data(self):
        """get parsed data for chart"""
        if self.user_options['charttype'] == 'time':
            parsed = self.time_chart_data()
        else:
            user_dict = self.generate_graph_data()
            df_chart = self.resize_chart(self.df_period_chart(user_dict))
            result = df_chart.to_json(orient="split")
            parsed = json.loads(result)
            # overwrite 'data' ordered by types and not dates
            smoke_data = df_chart[df_chart.columns[0]].to_list()
            activity_data = df_chart[df_chart.columns[1]].to_list()
            parsed["data"] = {'base':smoke_data, 'activity':activity_data}
            parsed["min_cig"] = UserProfile.objects.get(user=self.user).starting_nb_cig
        return parsed
