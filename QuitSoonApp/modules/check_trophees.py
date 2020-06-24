#!/usr/bin/env python

import datetime
from datetime import datetime as dt
from datetime import date
import calendar
import pandas as pd
from django.contrib.auth.models import User
from django.db import IntegrityError

from QuitSoonApp.models import Trophee


class Trophee_checking:

    def __init__(self, stats):
        self.stats = stats
        # self.df = smoking_values_per_dates_with_all_dates_df(self.all_dates, self.values_per_dates)
        # self.user_futur_month_trophees = check_trophees_to_be_complete([30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330])
        # self.user_futur_days_trophees = self.check_trophees_to_be_complete([1, 2, 3, 4, 7, 10, 15, 20, 25])
        # self.trophee_to_create = self.check_days_trophees + self.check_month_trophees

    @property
    def values_per_dates(self):
        """ get smoking values in a dataframe """
        qs = self.stats.user_conso_full_days.values()
        data_cig = pd.DataFrame(qs)
        # combine stae_cig and time_cig into a datetime column
        data_cig['date'] = data_cig.apply(lambda r : dt.combine(r['date_cig'],r['time_cig']),1)
        # get nb_cig per date sorted
        nb_cig_per_date_serie = data_cig.date.dt.date.value_counts().sort_index()
        # rename serie to nb_cig
        nb_cig_per_date_serie.rename("nb_cig", inplace=True)
        nb_cig_per_date_serie.index.name = 'date'
        # convert serie to dataframe
        return nb_cig_per_date_serie.to_frame()

    @property
    def all_dates(self):
        ### get dataframe with all dates ###
        all_days_df = pd.DataFrame(self.stats.list_dates, columns=['date']).set_index('date')
        all_days_df.index = pd.to_datetime(all_days_df.index)
        return all_days_df

    def smoking_values_per_dates_with_all_dates_df(self, all_days_df, nb_cig_per_date_df):
        # concats in dataframe and format as needed
        nb_cig_per_date_df = pd.concat([all_days_df, nb_cig_per_date_df], axis=1)
        nb_cig_per_date_df.reset_index(inplace=True)
        return nb_cig_per_date_df

    ##### consecutive dates without smoking #####

    @property
    def get_nans_occurence(self):
        # get NaNs occurence in nb_cig_per_date_df
        return self.df.nb_cig.isnull().groupby(self.df.nb_cig.notnull().cumsum()).sum()

    # check if trophee already exists and remove it from trophee to succeed list
    def check_trophees_to_be_complete(self, list_trophees):
        final_list = []
        for trophee in list_trophees:
            if not Trophee.objects.filter(user=user, nb_cig=0, nb_jour=trophee).exists():
                final_list.append(trophee)
        return final_list

    @property
    def check_days_trophees(self):
        ##################### non smoking days trophees ######################################
        # for element in occurence de NaNs, check if >= element in trophee to succeed list
        # break it as soon as list completly checked
        trophee_to_create = []
        while True:
            if self.user_futur_days_trophees:
                for element in self.get_nans_occurence:
                    for trophee in self.user_futur_days_trophees:
                        if element >= trophee:
                            trophee_to_create.append(trophee)
                            if trophee == self.user_futur_days_trophees[-1]:
                                break
            break
        return trophee_to_create

    @property
    def parse_smoking_month(self):
        ##################### non smoking month trophees ######################################
        # month trophees are saved as %30
        ### for each month check if not smoked ###

        if self.user_futur_month_trophees:
            non_smoking_month = []
            for index, value in nb_cig_per_date_df.date.dt.month.value_counts().sort_index().items():
                # if full month
                if value == calendar.monthrange(2020, index)[1]:
                    # Get True if all data in this month are NaNs
                    filter_month = nb_cig_per_date_df[(nb_cig_per_date_df.date.dt.month == index)].isnull().values.any()
                    if filter_month:
                        ## one month without smoking
                        non_smoking_month.append(True)
                        print(index, value, True)
                    else:
                        non_smoking_month.append(False)
                        print(index, value, False)
                else:
                    non_smoking_month.append(False)
                    print(index, value, False)
        return non_smoking_month

    @property
    def check_month_trophees(self):
        trophee_to_create = []
        non_smoking_month = self.parse_smoking_month
        while True:
            if self.user_futur_month_trophees:
                for trophee in self.user_futur_month_trophees:
                    compared_month = int((trophee / 30) - 1)
                    try:
                        if any(non_smoking_month[i]==non_smoking_month[i+compared_month] for i in range(len(non_smoking_month)-1)):
                            trophee_to_create.append(trophee)
                    except IndexError: #no enough month passed to get trophees
                        pass
                    if trophee == self.user_futur_month_trophees[-1]:
                        break
            break
        return trophee_to_create
