#!/usr/bin/env python

"""Module dedicated to stats calculation functions"""


import datetime
import calendar
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from dateutil import rrule
import pytz

from django.utils.timezone import make_aware
from django.db.models import Sum
from django.utils import timezone

from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    ConsoAlternative
    )


class Stats:
    """
    Class dedicated to stats calculation functions common for smoke and health
    """
    def __init__(self, user, lastday, tz_offset):
        self.user = user
        self.tz_offset = tz_offset
        self.datetime_start = self.get_datetime_start()
        self.lastday = self.get_last_day(lastday)
        self.nb_full_days_since_start = (lastday - self.datetime_start).days

    @property
    def starting_nb_cig(self):
        """starting_nb_cig in profile or 0"""
        if UserProfile.objects.filter(user=self.user).exists():
            return UserProfile.objects.get(user=self.user).starting_nb_cig
        return 0

    @property
    def first_day(self):
        """first day using app, Bool"""
        if self.nb_full_days_since_start:
            return False
        return True

    def get_last_day(self, lastday):
        """get lastday without timedelta client tz_offset"""
        if self.tz_offset:
            return lastday - timedelta(minutes=self.tz_offset)
        return lastday

    def get_datetime_start(self):
        """
        user only gave date in order to simplifie UX
        so find first time of this date or set it at noon
        """

        first_smoke = ConsoCig.objects.filter(user=self.user).first()
        first_alter = ConsoAlternative.objects.filter(user=self.user).first()

        if first_smoke and first_alter:
            min_conso_dt = min(first_smoke.datetime_cig, first_alter.datetime_alter)
        else:
            if first_smoke:
                min_conso_dt = first_smoke.datetime_cig
            elif first_alter:
                min_conso_dt = first_alter.datetime_alter
            else:
                min_conso_dt = None

        if UserProfile.objects.filter(user=self.user).exists():
            date_start = UserProfile.objects.get(user=self.user).date_start
            dt_start = datetime.datetime.combine(date_start, datetime.time(12, 0))
            dt_start_aware = make_aware(dt_start, pytz.utc)
            if min_conso_dt:
                if min_conso_dt.date() == date_start:
                    return min_conso_dt - timedelta(minutes=self.tz_offset)
            return dt_start_aware
        if min_conso_dt:
            return min_conso_dt - timedelta(minutes=self.tz_offset)
        return timezone.now()

    def daterange(self, start_date, end_date):
        """generate all dates from start_date to end_date """
        current_tz = timezone.get_current_timezone()
        start_date = current_tz.normalize(self.datetime_start.astimezone(current_tz))
        end_date = current_tz.normalize(self.lastday.astimezone(current_tz))
        for num in range(int ((end_date - start_date + timedelta(1)).days)):
            yield start_date + timedelta(num)

    @property
    def list_dates(self):
        """list of all dates from day user started app and last_day in argument """
        list_dates = []
        start_date = self.datetime_start
        end_date = self.lastday
        for single_date in self.daterange(start_date, end_date):
            list_dates.append(single_date.date())
        if self.lastday.date() not in list_dates:
            list_dates.append(self.lastday.date())
        return list_dates

    def nb_full_period_for_average(self, date, period):
        """ get number of achieve full periods (days, weeks or months) since start """
        # # get the day before to get last full day
        lastfullday = date - timedelta(1)
        if period == 'week':
            weeks = rrule.rrule(rrule.WEEKLY, dtstart=self.datetime_start.date(), until=lastfullday)
            return weeks.count() - 1 # - current week
        if period == 'month':
            # get first day of month to calculte number of full months
            if self.datetime_start.day == 1:
                day_1_of_month = self.datetime_start.date()
            else:
                day_1_of_month = self.datetime_start.date().replace(day=1) + relativedelta(months=1)
            # get last day of month to calculate number of full months
            if lastfullday.day == calendar.monthrange(lastfullday.year,lastfullday.month)[1]:
                last_day_of_month = lastfullday
            else:
                last_month = lastfullday - relativedelta(months=1)
                last_day_of_month = datetime.date(
                    last_month.year,
                    last_month.month,
                    calendar.monthrange(last_month.year, last_month.month)[1]
                    )
            month = rrule.rrule(rrule.MONTHLY, dtstart=day_1_of_month, until=last_day_of_month)
            return month.count()
        # else, excpect day
        day = rrule.rrule(rrule.DAILY, dtstart=self.datetime_start.date(), until=lastfullday)
        return day.count()

class SmokeStats(Stats):
    """Generate stats reports on user smoke habits for past days"""

    def __init__(self, user, lastday, tz_offset):
        Stats.__init__(self, user, lastday, tz_offset)
        self.user_conso_all_days = ConsoCig.objects.filter(user=self.user)
        self.stats_user_conso = self.get_user_conso()
        self.update_dt_user_model_field()

    def get_user_conso(self):
        """
        get user conso depending on first day or not
        for stats often use only full days data except for the first day
        """
        date_range = (
            datetime.datetime.combine(
                self.lastday,
                datetime.datetime.min.time().replace(tzinfo=pytz.UTC)
                ),
            datetime.datetime.combine(
                self.lastday,
                datetime.datetime.max.time().replace(tzinfo=pytz.UTC)
                )
        )
        if self.first_day:
            return self.user_conso_all_days
        return self.user_conso_all_days.exclude(user_dt__range=date_range)

    def update_dt_user_model_field(self):
        """Update fielf user_dt with actual client tz_offset"""
        for conso in self.user_conso_all_days:
            conso.user_dt = conso.datetime_cig - timedelta(minutes=self.tz_offset)
            conso.save()

    def nb_per_day(self, date):
        """ nb smoke per day """
        date_range = (
            datetime.datetime.combine(date, datetime.datetime.min.time().replace(tzinfo=pytz.UTC)),
            datetime.datetime.combine(date, datetime.datetime.max.time().replace(tzinfo=pytz.UTC))
        )
        conso_day = self.user_conso_all_days.filter(user_dt__range=date_range)
        return conso_day.count()

    @property
    def total_smoke_all_days(self):
        """
        total number of cigarette smoked by user
        """
        return self.user_conso_all_days.count()

    @property
    def total_smoke(self):
        """
        total number of cigarette smoked by user
        """
        return self.stats_user_conso.count()

    @property
    def average_per_day(self):
        """ smoke average per day in full days smoke"""
        if self.first_day:
            return self.total_smoke
        return self.total_smoke / self.nb_full_days_since_start

    @property
    def count_smoking_day(self):
        """ number of days user smoked """
        smoked_days = self.stats_user_conso.order_by('user_dt__date')
        return smoked_days.distinct('user_dt__date').count()

    @property
    def count_no_smoking_day(self):
        """ number of day user didn't smoke """
        if self.first_day:
            return 1 - self.count_smoking_day
        return self.nb_full_days_since_start - self.count_smoking_day

    @property
    def total_cig_with_old_habits(self):
        """
        total of cigarette user would have smoke with old habit for past days
        (declared by user in profile in starting_nb_cig)
        """
        if self.first_day:
            return self.starting_nb_cig
        return self.starting_nb_cig * self.nb_full_days_since_start

    @property
    def nb_not_smoked_cig(self):
        """number of cigarette user didn't smoke compare to old_habits"""
        return self.total_cig_with_old_habits - self.total_smoke

    @property
    def no_smoking_day_list_dates(self):
        """
        list of day in which user didn't smoke in order to check if trophy accomplished
        so only look for full days and not current day
        """
        if not self.first_day:
            no_smoking_day_list_dates = []
            delta = self.lastday - self.datetime_start
            for i in range(delta.days + 1):
                day = self.datetime_start + timedelta(days=i)
                if not self.stats_user_conso.filter(user_dt__date=day).exists():
                    no_smoking_day_list_dates.append(day.date())
            return no_smoking_day_list_dates
        return None

    def money_smoked_per_day(self, date):
        """ total of money user spent the day in argument smoking cigarettes """
        conso_day = self.user_conso_all_days.filter(user_dt__date=date)
        money_smoked = 0
        for conso in conso_day:
            if conso.paquet:
                money_smoked += conso.paquet.price_per_cig
        return round(money_smoked, 2)

    @property
    def total_money_smoked(self):
        """total money since starting day user spent on cigarettes"""
        money_smoked = 0
        for conso in self.stats_user_conso:
            if conso.paquet:
                money_smoked += conso.paquet.price_per_cig
        return money_smoked

    @property
    def average_money_per_day(self):
        """ average money user spend per day smoking cigarettes """
        if self.first_day:
            return self.total_money_smoked
        return self.total_money_smoked / self.nb_full_days_since_start

    @property
    def total_money_with_starting_nb_cig(self):
        """
        total money since starting day user would have spent on cigarettes
        with old habits (declared by user in profile in starting_nb_cig)
        """
        money = 0
        #get first pack created
        first_pack = Paquet.objects.get(user=self.user, first=True)
        if self.first_day:
            money += first_pack.price_per_cig * self.starting_nb_cig
        else:
            money += self.nb_full_days_since_start * first_pack.price_per_cig * self.starting_nb_cig
        return money

    @property
    def money_saved(self):
        """
        compare money user would have spent on cigaretteswith old habits
        and money he/she actualy spent
        """
        money_saved = self.total_money_with_starting_nb_cig - self.total_money_smoked
        return round(money_saved, 2)


class HealthyStats(Stats):
    """Generate stats reports on user healthy habits"""

    def __init__(self, user, lastday, tz_offset):
        Stats.__init__(self, user, lastday, tz_offset)
        self.user_conso_all_days = ConsoAlternative.objects.filter(user=self.user)
        self.update_dt_user_model_field()
        self.stats_user_conso = self.user_conso_all_days.exclude(
            user_dt__range=(self.datetime_start, self.lastday)
            )
        self.user_activities = self.user_conso_all_days.exclude(alternative__type_alternative='Su')
        self.user_conso_subsitut = self.user_conso_all_days.filter(
            alternative__type_alternative='Su'
            )

    def update_dt_user_model_field(self):
        """Update fielf user_dt with actual client tz_offset"""
        for conso in self.user_conso_all_days:
            conso.user_dt = conso.datetime_alter - timedelta(minutes=self.tz_offset)
            conso.save()

    def filter_queryset_for_report(self, category='Ac', type_alt=None):
        """Filter queryset used to create stats"""
        if category == 'Ac':
            queryset = self.user_activities
            if type_alt:
                queryset = queryset.filter(alternative__type_activity=type_alt)
            return queryset
        if category == 'Su':
            queryset = self.user_conso_subsitut
            if type_alt:
                queryset = queryset.filter(alternative__substitut=type_alt)
            return queryset
        return None

    def report_alternative_per_period(self, date, category='Ac', period='day', type_alt=None):
        """
        For date, return for the period:
        time activities in minutes
        count substituts
        """
        # get based queryset
        queryset = self.filter_queryset_for_report(category, type_alt)
        if queryset:
            if category == 'Ac':
                queryset = self.filter_by_period(date, period, queryset)
                return queryset.aggregate(Sum('activity_duration'))['activity_duration__sum']
            if category == 'Su':
                queryset = self.filter_by_period(date, period, queryset)
                return queryset.count()
        return None

    @staticmethod
    def filter_by_period(date, period, queryset):
        """ filter queryset by period """
        if period == 'week':
            week_number = date.isocalendar()[1]
            return queryset.filter(user_dt__week=week_number)
        if period == 'month':
            return queryset.filter(user_dt__month=date.month)
        # excpect period == 'days'
        date_range = (
            datetime.datetime.combine(
                date,
                datetime.datetime.min.time().replace(tzinfo=pytz.UTC)
                ),
            datetime.datetime.combine(
                date,
                datetime.datetime.max.time().replace(tzinfo=pytz.UTC)
                )
        )
        return queryset.filter(user_dt__range=date_range)

    @staticmethod
    def convert_minutes_to_hours_min_str(minutes=0):
        """convert minutes type int into formated str"""
        try:
            if minutes:
                if minutes < 60:
                    return str(minutes) + ' minutes'
                return str(timedelta(minutes=minutes))[:-3].replace(':', 'h')
            return None
        except TypeError:
            return None

    def nicotine_per_day(self, date):
        """ nicotine in mg took the the day in argument """
        date_range = (
            datetime.datetime.combine(date, datetime.datetime.min.time().replace(tzinfo=pytz.UTC)),
            datetime.datetime.combine(date, datetime.datetime.max.time().replace(tzinfo=pytz.UTC))
        )
        conso_day = self.user_conso_subsitut.filter(user_dt__range=date_range)
        nicotine = 0
        for conso in conso_day:
            nicotine += conso.alternative.nicotine
        return nicotine
