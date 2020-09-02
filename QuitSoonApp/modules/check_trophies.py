#!/usr/bin/env python

import datetime
from datetime import datetime as dt
from datetime import date
import calendar
import pandas as pd
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import transaction

from QuitSoonApp.models import Trophy


class trophy_checking:

    def __init__(self, stats):
        self.stats = stats
        if stats.user_conso_full_days:
            self.df = self.smoking_values_per_dates_with_all_dates_df(self.all_dates, self.values_per_dates)
        self.challenges = {
            'conso' : {
                'nb_cig': [20, 15, 10, 5, 4, 3, 2, 1],
                'nb_days' : [3, 7]
                },
            'zero_cig': {
                'nb_cig': [0],
                'nb_days': [1, 2, 3, 4, 7, 10, 15, 20, 25, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
                },
            }
        # initialise all_user_challenges in a dict with bool in trophies or ot
        self.user_trophies = self.all_user_challenges_before_parsing

    @property
    def all_user_challenges_before_parsing(self):
        """"""
        challenges_dict = {}
        for type, challenge in self.challenges.items():
            for cig in challenge['nb_cig']:
                # only challenges with less cig then usual user conso
                if cig < self.stats.starting_nb_cig:
                    for days in challenge['nb_days']:
                        # only if challenge not already saved as trophy in db
                        if Trophy.objects.filter(user=self.stats.user, nb_cig=cig, nb_jour=days).exists():
                            challenges_dict[(cig, days)] = True
                        else:
                            challenges_dict[(cig, days)] = False
        return challenges_dict

    @property
    def values_per_dates(self):
        """ get count cig smoked (col nb_cig) per dates(index) in DataFrame """
        qs = self.stats.user_conso_full_days.values()
        data_cig = pd.DataFrame(qs)
        # get nb_cig per date sorted
        nb_cig_per_date_serie = data_cig.user_dt.dt.date.value_counts().sort_index()
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

    def get_conso_occurence(self, challenge):
        """get occurence conso lower than challenge"""
        self.df['lower'] = self.df['nb_cig'].apply(lambda x: False if x > challenge else True)
        lower = self.df.lower
        self.df['upper'] = self.df['nb_cig'].apply(lambda x: True if x > challenge else False)
        upper = self.df.upper
        return lower.groupby(upper.cumsum()).sum()

    def get_nans_occurence(self):
        """ get NaNs occurence in dataframe """
        return self.df.nb_cig.isnull().groupby(self.df.nb_cig.notnull().cumsum()).sum()

    @property
    def list_user_challenges(self):
        """
        get challenges in a list of tupples (nb_cig, nb_consecutive_days)
        take only relevant challenge to check
        """
        challenges_list = []
        for challenge, success in self.all_user_challenges_before_parsing.items():
            # only if challenge not already saved as trophy in db
            if not success:
                challenges_list.append((challenge[0], challenge[1]))
        return challenges_list

    @property
    def trophies_accomplished(self):
        """ get list of trophies accomplished by user and to be created in DB """
        new_trophies = []
        if self.stats.user_conso_full_days:
            # only modify trophies if user
            for challenge in self.list_user_challenges:

                # if not enough days in user history, challenge = False
                if challenge[1] >= self.stats.nb_full_days_since_start:
                    pass
                else:
                    # treatement differs if days or month
                    if challenge[1] < 30:
                        new = self.check_days_trophies(challenge)
                        if new:
                            self.user_trophies[challenge] = new
                            new_trophies.append(challenge)
                    else:
                        new = self.check_month_trophies(challenge[1])
                        if new:
                            self.user_trophies[challenge] = new
                            new_trophies.append(challenge)
        return new_trophies

    def check_days_trophies(self, challenge):
        """
        ##################### non smoking days trophies #########################
        for element in occurence, check if >= element in trophy to succeed
        """
        if challenge[0] > 0:
            occurence = self.get_conso_occurence(challenge[0])
        else:
            occurence = self.get_nans_occurence()
        for element in occurence:
            if element >= challenge[1]:
                return True
        return False

    def check_month_trophies(self, nb_jour):
        """
        ##################### non smoking month trophies #####################
        check if completed trophies months without smoking
        """
        non_smoking_month = self.parse_smoking_month
        compared_month = range(int((nb_jour) / 30 - 1))
        # for each bool non_smoking_month => True if full month and no smoking
        # compare with following bool
        while True:
            for i in range(len(non_smoking_month)):
                compare = [non_smoking_month[i]]
                n = 0
                # based on trophy compared following data would be different size
                for month in compared_month:
                    try:
                        n+=1
                        compare.append(non_smoking_month[i+n])
                    except IndexError:
                        # comparing data out of list index, pass next trophy checking
                        break
                if not False in compare:
                    # only full month and non smoked, break to pass next trophy checking
                    return True
            # end index in non_smoking_month, pass next trophy checking
            break
        return False


    @property
    def parse_smoking_month(self):
        """
        for each month check if full and not smoking (True), else False
        """
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

    def create_trophies(self):
        """create new trophies"""
        for trophy in self.trophies_accomplished:
            try:
                with transaction.atomic():
                    Trophy.objects.create(user=self.stats.user, nb_cig=trophy[0], nb_jour=trophy[1])
            except IntegrityError:
                # method already called
                pass
