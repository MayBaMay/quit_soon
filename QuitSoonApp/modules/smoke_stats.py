#!/usr/bin/env python

from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from QuitSoonApp.models import UserProfile, Paquet, ConsoCig, ConsoAlternative

class Stats:
    def __init__(self, user, lastday):
        self.user = user
        self.lastday = lastday
        self.date_start = UserProfile.objects.get(user=self.user).date_start
        self.starting_nb_cig = UserProfile.objects.get(user=self.user).starting_nb_cig
        self.nb_jour_since_start = (self.lastday - self.date_start).days + 1

class SmokeStats(Stats):
    """Generate stats reports on user smoke habits"""

    def __init__(self, user, lastday):
        Stats.__init__(self, user, lastday)
        self.user_conso = ConsoCig.objects.filter(user=self.user)

    def nb_per_day(self, date):
        """ nb smoke per day """
        conso_day = self.user_conso.filter(date_cig=date)
        return conso_day.count()

    @property
    def total_smoke(self):
        """ total number of cigarette smoked by user"""
        return self.user_conso.count()

    @property
    def average_per_day(self):
        """ smoke average per day """
        return self.total_smoke / self.nb_jour_since_start

    @property
    def count_smoking_day(self):
        """ number of day user smoked """
        smoking_days = ConsoCig.objects.order_by('date_cig').distinct('date_cig')
        return smoking_days.count()

    @property
    def count_no_smoking_day(self):
        """ number of day user didn't smoke """
        return self.nb_jour_since_start - self.count_smoking_day

    @property
    def total_cig_with_old_habits(self):
        """
        total of cigarette user would have smoke with old habit
        (declared by user in profile in starting_nb_cig)
        """
        return self.starting_nb_cig * self.nb_jour_since_start

    @property
    def nb_not_smoked_cig(self):
        return self.total_cig_with_old_habits - self.total_smoke

    @staticmethod
    def daterange(start_date, end_date):
        """generate all dates from start_date to end_date """
        start_date = start_date
        for n in range(int ((end_date - start_date + timedelta(1)).days)):
            yield start_date + timedelta(n)

    @property
    def list_dates(self):
        """list of all dates from day user started app and last_day in argument """
        list_dates = []
        start_date = datetime.combine(self.date_start, datetime.min.time())
        end_date = datetime.combine(self.lastday, datetime.min.time())
        for single_date in self.daterange(start_date, end_date):
            list_dates.append(single_date.date())
        return list_dates

    @property
    def no_smoking_day_list_dates(self):
        """ list of day in which user didn't smoke """
        no_smoking_day_list_dates = []
        start = datetime.combine(self.date_start, datetime.min.time())
        lastday = datetime.combine(self.lastday, datetime.min.time())
        delta =  lastday - start
        for i in range(delta.days + 1):
            day = start + timedelta(days=i)
            if not self.user_conso.filter(date_cig=day).exists():
                no_smoking_day_list_dates.append(day.date())
        return no_smoking_day_list_dates

    def money_smoked_per_day(self, date):
        """ total of money user spent the day in argument smoking cigarettes """
        conso_day = self.user_conso.filter(date_cig=date)
        money_smoked = 0
        for conso in conso_day:
            if conso.paquet:
                money_smoked += conso.paquet.price_per_cig
        return money_smoked

    @property
    def average_money_per_day(self):
        """ average money user spend per day smoking cigarettes """
        return self.total_money_smoked / self.nb_jour_since_start

    @property
    def total_money_smoked(self):
        """total money since starting day user spent on cigarettes"""
        money_smoked = 0
        for conso in self.user_conso:
            if conso.paquet:
                money_smoked += conso.paquet.price_per_cig
        return money_smoked

    @property
    def total_money_with_starting_nb_cig(self):
        """
        total money since starting day user would have spent on cigarettes
        with old habits (declared by user in profile in starting_nb_cig)
        """
        money = 0
        #get first pack created
        first_pack = Paquet.objects.get(user=self.user, first=True)
        money += self.nb_jour_since_start * first_pack.price_per_cig * self.starting_nb_cig
        return money

    @property
    def money_saved(self):
        """
        compare money user would have spent on cigaretteswith old habits
        and money he/she actualy spent
        """
        return self.total_money_with_starting_nb_cig - self.total_money_smoked


class HealthyStats(Stats):
    """Generate stats reports on user healthy habits"""

    def __init__(self, user, lastday):
        Stats.__init__(self, user, lastday)
        self.user_conso = ConsoAlternative.objects.filter(user=self.user)

    def min_per_day(self, date):
        """ time in minutes spent the day in argument for healthy activities """
        user_activities = self.user_conso.exclude(alternative__type_alternative='Su')
        activity_day = user_activities.filter(date_alter=date)
        min_activity = 0
        for activity in activity_day:
            min_activity += activity.activity_duration
        return min_activity
