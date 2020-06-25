#!/usr/bin/env python

import datetime
from datetime import datetime as dt
from datetime import date
import calendar
import pandas as pd
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import transaction


from QuitSoonApp.models import Trophee


class Trophee_checking:

    def __init__(self, stats):
        self.stats = stats
        self.df = self.smoking_values_per_dates_with_all_dates_df(self.all_dates, self.values_per_dates)
        self.user_futur_month_trophees = self.check_trophees_to_be_completed([30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330])
        self.user_futur_days_trophees = self.check_trophees_to_be_completed([1, 2, 3, 4, 7, 10, 15, 20, 25])
        self.trophees_to_create = self.check_days_trophees + self.check_month_trophees

    @property
    def values_per_dates(self):
        """ get count cig smoked (col nb_cig) per dates(index) in DataFrame """
        qs = self.stats.user_conso_full_days.values()
        data_cig = pd.DataFrame(qs)
        # combine stae_cig and time_cig into a datetime column
        data_cig['date'] = data_cig.apply(lambda r : dt.combine(r['date_cig'],r['time_cig']),1)
        # get nb_cig per date sorted
        nb_cig_per_date_serie = data_cig.date.dt.date.value_counts().sort_index()
        # rename serie to nb_cig and index to date
        nb_cig_per_date_serie.rename("nb_cig", inplace=True)
        nb_cig_per_date_serie.index.name = 'date'
        # convert date to datetime
        nb_cig_per_date_serie.index = pd.to_datetime(nb_cig_per_date_serie.index)
        # convert serie to dataframe
        return nb_cig_per_date_serie.to_frame()

    @property
    def all_dates(self):
        """get all passed dates, index of empty dataframe"""
        ### get dataframe with all dates ###
        all_days_df = pd.DataFrame(self.stats.list_dates, columns=['date']).set_index('date')
        # take out the current day (only full pasts days)
        all_days_df.drop(all_days_df.tail(1).index,inplace=True)
        # convert date to datetime
        all_days_df.index = pd.to_datetime(all_days_df.index)
        return all_days_df

    def smoking_values_per_dates_with_all_dates_df(self, all_days_df, nb_cig_per_date_df):
        """
        get dataframe with all passed dates(index) and count cig per dates (col nb_cig)
        """
        # concats in dataframe and format as needed
        nb_cig_per_date_df = pd.concat([all_days_df, nb_cig_per_date_df], axis=1)
        nb_cig_per_date_df.reset_index(inplace=True)
        return nb_cig_per_date_df

    ##### consecutive dates without smoking #####

    @property
    def get_nans_occurence(self):
        """ get NaNs occurence in dataframe """
        return self.df.nb_cig.isnull().groupby(self.df.nb_cig.notnull().cumsum()).sum()


    def check_trophees_to_be_completed(self, list_trophees):
        """get trophees user didn't completed yet in a list"""
        # check if trophee already exists and get trophee not yet succeeded in a list
        final_list = []
        for trophee in list_trophees:
            if not Trophee.objects.filter(user=self.stats.user, nb_cig=0, nb_jour=trophee).exists():
                final_list.append(trophee)
        return final_list

    @property
    def check_days_trophees(self):
        """
        ##################### non smoking days trophees ######################################
        for element in occurence de NaNs, check if >= element in trophee to succeed list
        break it as soon as list completly checked
        """
        trophee_to_create = []
        while True:
            if self.user_futur_days_trophees:
                for element in self.get_nans_occurence:
                    for trophee in self.user_futur_days_trophees:
                        if not trophee in trophee_to_create:
                            if element >= trophee:
                                trophee_to_create.append(trophee)
                                if trophee == self.user_futur_days_trophees[-1]:
                                    break
            break
        return trophee_to_create

    @property
    def parse_smoking_month(self):
        """
        ##################### non smoking month trophees ######################################
        for each month check if full and not smoking (True), else False
        """
        if self.user_futur_month_trophees:
            non_smoking_month = []
            # proceed year after year to get appropriate calendar
            for year in self.df.date.dt.year.drop_duplicates().tolist():
                df_year = self.df[self.df.date.dt.year == year]
                for index, value in df_year.date.dt.month.value_counts().sort_index().items():
                    # if full month
                    if value == calendar.monthrange(year, index)[1]:
                        # Get True if all data in this month are NaNs
                        nb_Nans_in_month = df_year[(df_year.date.dt.month == index)].isnull().sum().nb_cig
                        total_rows_in_month = df_year[(df_year.date.dt.month == index)].shape[0]
                        if nb_Nans_in_month == total_rows_in_month:
                            ## one month without smoking
                            non_smoking_month.append(True)
                        else:
                            non_smoking_month.append(False)
                    else:
                        non_smoking_month.append(False)
            return non_smoking_month

    @property
    def check_month_trophees(self):
        """check if completed trophees months without smoking"""
        trophee_to_create = []
        non_smoking_month = self.parse_smoking_month
        # follow only if user still have trophees to complete
        if self.user_futur_month_trophees:
            for trophee in self.user_futur_month_trophees:
                while True:
                    # month trophees are %30
                    compared_month = range(int((trophee / 30) - 1))
                    # for each bool non_smoking_month => True if full month and no smoking
                    # compare with following bool
                    for i in range(len(non_smoking_month)):
                        compare = [non_smoking_month[i]]
                        n = 0
                        # based on trophee compared following data would be different size
                        for month in compared_month:
                            try:
                                n+=1
                                compare.append(non_smoking_month[i+n])
                            except IndexError:
                                # comparing data out of list index, pass next trophee checking
                                break
                        if not False in compare:
                            # only full month and non smoked, break to pass next trophee checking
                            trophee_to_create.append(trophee)
                            break
                    # end index in non_smoking_month, pass next trophee checking
                    break
        return trophee_to_create

    def create_trophees_no_smoking(self):
        for trophee in self.trophees_to_create:
            try:
                with transaction.atomic():
                    Trophee.objects.create(user=self.stats.user, nb_cig=0, nb_jour=trophee)
            except IntegrityError:
                # method already called
                pass
