#!/usr/bin/env python

from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.db.models import Sum

from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative
    )

class Stats:
    def __init__(self, user, lastday):
        self.user = user
        self.lastday = lastday
        self.date_start = UserProfile.objects.get(user=self.user).date_start
        self.starting_nb_cig = UserProfile.objects.get(user=self.user).starting_nb_cig
        self.nb_full_days_since_start = (self.lastday - self.date_start).days

    def nb_full_period_for_average(self, date, period):
        if period == 'day':
            # get the day before to get last full day
            yesterday = date - timedelta(1)
            # delta between yesterday and first day app
            delta = yesterday - self.date_start
            # return nb days
            return delta.days
        if period == 'week':
            # get week number last (full) week
            last_week = date.isocalendar()[1] - 1
            first_week = self.date_start.isocalendar()[1]
            return last_week - first_week
        if period == 'month':
            last_month = date.month - 1
            first_month = self.date_start.month
            return last_month - first_month


class SmokeStats(Stats):
    """Generate stats reports on user smoke habits for past days"""

    def __init__(self, user, lastday):
        Stats.__init__(self, user, lastday)
        self.user_conso_all_days = ConsoCig.objects.filter(user=self.user)
        self.user_conso_full_days = self.user_conso_all_days.exclude(date_cig=self.lastday)

    def nb_per_day(self, date):
        """ nb smoke per day """
        conso_day = self.user_conso_all_days.filter(date_cig=date)
        return conso_day.count()

    @property
    def total_smoke_all_days(self):
        """
        total number of cigarette smoked by user
        """
        return self.user_conso_all_days.count()

    @property
    def total_smoke_full_days(self):
        """
        total number of cigarette smoked by user
        """
        return self.user_conso_full_days.count()

    @property
    def average_per_day(self):
        """ smoke average per day in full days smoke"""
        try:
            return self.total_smoke_full_days / self.nb_full_days_since_start
        except ZeroDivisionError:
            # 1st day so no full days
            return None

    @property
    def count_smoking_day(self):
        """ number of days user smoked """
        distinct_date_cig = ConsoCig.objects.order_by('date_cig').distinct('date_cig')
        return distinct_date_cig.exclude(date_cig=self.lastday).count()

    @property
    def count_no_smoking_day(self):
        """ number of day user didn't smoke """
        return self.nb_full_days_since_start - self.count_smoking_day

    @property
    def total_cig_with_old_habits(self):
        """
        total of cigarette user would have smoke with old habit for past days
        (declared by user in profile in starting_nb_cig)
        """
        return self.starting_nb_cig * self.nb_full_days_since_start

    @property
    def nb_not_smoked_cig_full_days(self):
        return self.total_cig_with_old_habits - self.total_smoke_full_days

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
            if not self.user_conso_full_days.filter(date_cig=day).exists():
                no_smoking_day_list_dates.append(day.date())
        return no_smoking_day_list_dates

    def money_smoked_per_day(self, date):
        """ total of money user spent the day in argument smoking cigarettes """
        conso_day = self.user_conso_all_days.filter(date_cig=date)
        money_smoked = 0
        for conso in conso_day:
            if conso.paquet:
                money_smoked += conso.paquet.price_per_cig
        return round(money_smoked, 2)

    @property
    def total_money_smoked_full_days(self):
        """total money since starting day user spent on cigarettes"""
        money_smoked = 0
        for conso in self.user_conso_full_days:
            if conso.paquet:
                money_smoked += conso.paquet.price_per_cig
        return money_smoked

    @property
    def average_money_per_day_full_days(self):
        """ average money user spend per day smoking cigarettes """
        try:
            return self.total_money_smoked_full_days / self.nb_full_days_since_start
        except ZeroDivisionError:
            # 1st day so no full days
            return None

    @property
    def total_money_with_starting_nb_cig(self):
        """
        total money since starting day user would have spent on cigarettes
        with old habits (declared by user in profile in starting_nb_cig)
        """
        money = 0
        #get first pack created
        first_pack = Paquet.objects.get(user=self.user, first=True)
        money += self.nb_full_days_since_start * first_pack.price_per_cig * self.starting_nb_cig
        return money

    @property
    def money_saved_full_days(self):
        """
        compare money user would have spent on cigaretteswith old habits
        and money he/she actualy spent
        """
        money_saved = self.total_money_with_starting_nb_cig - self.total_money_smoked_full_days
        return round(money_saved, 2)


class HealthyStats(Stats):
    """Generate stats reports on user healthy habits"""

    def __init__(self, user, lastday):
        Stats.__init__(self, user, lastday)
        self.user_conso_all_days = ConsoAlternative.objects.filter(user=self.user)
        self.user_conso_full_days = self.user_conso_all_days.exclude(date_alter=self.lastday)
        self.user_activities = self.user_conso_all_days.exclude(alternative__type_alternative='Su')
        self.user_conso_subsitut = self.user_conso_all_days.filter(alternative__type_alternative='Su')

    def filter_queryset_for_report(self, category='Ac', type=None):
        if category == 'Ac':
            queryset = self.user_activities
            if type:
                queryset = queryset.filter(alternative__type_activity=type)
            return queryset
        elif category == 'Su':
            queryset = self.user_conso_subsitut
            if type:
                queryset = queryset.filter(alternative__substitut=type)
            return queryset
        else:
            return None

    def report_substitut_per_period(self, date, category='Ac', period='day', type=None):
        """
        For date, return for the period:
        time activities in minutes
        count substituts
        """
        # get based queryset
        queryset = self.filter_queryset_for_report(category, type)
        if queryset:
            if category == 'Ac':
                queryset = self.filter_by_period(date, period, queryset)
                return queryset.aggregate(Sum('activity_duration'))['activity_duration__sum']
            elif category == 'Su':
                queryset = self.filter_by_period(date, period, queryset)
                return queryset.count()
        return None

    def report_substitut_average_per_period(self, date, category='Ac', period='day', type=None):
        # get only full days data so exclude today
        queryset = self.filter_queryset_for_report(category, type).exclude(date_alter=date)
        try:
            if category == 'Ac':
                sum = queryset.aggregate(Sum('activity_duration'))['activity_duration__sum']
                return sum / self.nb_full_period_for_average(date, period)
            elif category == 'Su':
                count = queryset.count()
                return count / self.nb_full_period_for_average(date, period)
            else:
                return None
        except ZeroDivisionError:
            # 1st day so no full days
            return None

    def filter_by_period(self, date, period, queryset):
        # filter by period
        if period == 'day':
            return queryset.filter(date_alter=date)
        elif period == 'week':
            week_number = date.isocalendar()[1]
            return queryset.filter(date_alter__week=week_number)
        elif period == 'month':
            return queryset.filter(date_alter__month=date.month)


    @staticmethod
    def convert_minutes_to_hours_min_str(minutes):
        """convert minutes type int into formated str"""
        if minutes:
            if minutes < 60:
                return str(minutes) + ' minutes'
            return str(timedelta(minutes=minutes))[:-3].replace(':', 'h')
        return None

    def nicotine_per_day(self, date):
        """ nicotine in mg took the the day in argument """
        conso_day = self.user_conso_subsitut.filter(date_alter=date)
        nicotine = 0
        for conso in conso_day:
            nicotine += conso.alternative.nicotine
        return nicotine
