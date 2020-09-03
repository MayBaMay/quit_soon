#!/usr/bin/env python

import datetime
from datetime import timedelta
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import calendar
import pytz

from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.db.models import Sum
from django.utils import timezone

from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative
    )

class Stats:
    def __init__(self, user, lastday, tz_offset):
        self.profile = UserProfile.objects.filter(user=user).exists()
        self.user = user
        if tz_offset:
            self.tz_offset = tz_offset
            self.lastday = lastday - timedelta(minutes=tz_offset)
        else:
            self.tz_offset = 0
            self.lastday = lastday
        self.datetime_start = self.get_datetime_start()
        if self.profile:
            self.starting_nb_cig = UserProfile.objects.get(user=self.user).starting_nb_cig
        else:
            self.starting_nb_cig = 0
        self.nb_full_days_since_start = (self.lastday - self.datetime_start).days
        if self.nb_full_days_since_start:
            self.first_day = False
        else:
            self.first_day = True

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

        if self.profile:
            date_start = UserProfile.objects.get(user=self.user).date_start
            dt_start = datetime.datetime.combine(date_start, datetime.time(12, 0))
            dt_start_aware = make_aware(dt_start, pytz.utc)
            if min_conso_dt:
                if min_conso_dt.date() == date_start:
                    return min_conso_dt - timedelta(minutes=self.tz_offset)
            return dt_start_aware
        else:
            if min_conso_dt:
                return min_conso_dt - timedelta(minutes=self.tz_offset)
            else:
                return timezone.now()

    def nb_full_period_for_average(self, date, period):
        """ get number of achieve full periods (days, weeks or months) since start """
        # # get the day before to get last full day
        lastfullday = date - timedelta(1)
        if period == 'day':
            day = rrule.rrule(rrule.DAILY, dtstart=self.datetime_start.date(), until=lastfullday)
            return day.count()
        if period == 'week':
            weeks = rrule.rrule(rrule.WEEKLY, dtstart=self.datetime_start.date(), until=lastfullday)
            return weeks.count() - 1 # - current week

        if period == 'month':
            # get first day of month to calculte number of full months
            if self.datetime_start.day == 1:
                first_day_of_month = self.datetime_start.date()
            else:
                first_day_of_month = self.datetime_start.date().replace(day=1) + relativedelta(months=1)
            # get last day of month to calculate number of full months
            if lastfullday.day == calendar.monthrange(lastfullday.year,lastfullday.month)[1]:
                last_day_of_month = lastfullday
            else:
                last_month = lastfullday - relativedelta(months=1)
                last_day_of_month = datetime.date(last_month.year, last_month.month, calendar.monthrange(last_month.year, last_month.month)[1])
            month = rrule.rrule(rrule.MONTHLY, dtstart=first_day_of_month, until=last_day_of_month)
            return month.count()


class SmokeStats(Stats):
    """Generate stats reports on user smoke habits for past days"""

    def __init__(self, user, lastday, tz_offset):
        Stats.__init__(self, user, lastday, tz_offset)
        self.user_conso_all_days = ConsoCig.objects.filter(user=self.user)
        self.update_dt_user_model_field()
        date_range = (
            datetime.datetime.combine(self.lastday, datetime.datetime.min.time().replace(tzinfo=pytz.UTC)),
            datetime.datetime.combine(self.lastday, datetime.datetime.max.time().replace(tzinfo=pytz.UTC))
        )
        self.user_conso_full_days = self.user_conso_all_days.exclude(user_dt__range=date_range)

    def update_dt_user_model_field(self):
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
    def total_smoke_full_days(self):
        """
        total number of cigarette smoked by user
        """
        return self.user_conso_full_days.count()

    @property
    def average_per_day(self):
        """ smoke average per day in full days smoke"""
        if self.first_day:
            return self.total_smoke_all_days
        else:
            return self.total_smoke_full_days / self.nb_full_days_since_start

    @property
    def count_smoking_day(self):
        """ number of days user smoked """
        if self.first_day:
            return self.user_conso_all_days.order_by('user_dt__date').distinct('user_dt__date').count()
        else:
            return self.user_conso_full_days.order_by('user_dt__date').distinct('user_dt__date').count()

    @property
    def count_no_smoking_day(self):
        """ number of day user didn't smoke """
        if self.first_day:
            return 1 - self.count_smoking_day
        else:
            return self.nb_full_days_since_start - self.count_smoking_day

    @property
    def total_cig_with_old_habits(self):
        """
        total of cigarette user would have smoke with old habit for past days
        (declared by user in profile in starting_nb_cig)
        """
        if self.first_day:
            return self.starting_nb_cig
        else:
            return self.starting_nb_cig * self.nb_full_days_since_start

    @property
    def nb_not_smoked_cig_full_days(self):
        if self.first_day:
            return self.total_cig_with_old_habits - self.total_smoke_all_days
        else:
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
        start_date = self.datetime_start
        end_date = self.lastday
        for single_date in self.daterange(start_date, end_date):
            list_dates.append(single_date.date())
        return list_dates

    @property
    def no_smoking_day_list_dates(self):
        """
        list of day in which user didn't smoke in order to check if trophy accomplished
        so only look for full days and not current day
        """
        no_smoking_day_list_dates = []
        delta = self.lastday - self.datetime_start
        for i in range(delta.days + 1):
            day = self.datetime_start + timedelta(days=i)
            if not self.user_conso_full_days.filter(user_dt__date=day).exists():
                no_smoking_day_list_dates.append(day.date())
        return no_smoking_day_list_dates

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
        if self.first_day:
            user_conso = self.user_conso_all_days
        else:
            user_conso = self.user_conso_full_days
        for conso in user_conso:
            if conso.paquet:
                money_smoked += conso.paquet.price_per_cig
        return money_smoked

    @property
    def average_money_per_day(self):
        """ average money user spend per day smoking cigarettes """
        if self.first_day:
            return self.total_money_smoked
        else:
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
        self.user_conso_full_days = self.user_conso_all_days.exclude(user_dt__range=(self.datetime_start, self.lastday))
        self.user_activities = self.user_conso_all_days.exclude(alternative__type_alternative='Su')
        self.user_conso_subsitut = self.user_conso_all_days.filter(alternative__type_alternative='Su')

    def update_dt_user_model_field(self):
        for conso in self.user_conso_all_days:
            conso.user_dt = conso.datetime_alter - timedelta(minutes=self.tz_offset)
            conso.save()

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

        if self.first_day:
            queryset = self.filter_queryset_for_report(category, type)
        else:
            # get only full days data so exclude today
            queryset = self.filter_queryset_for_report(category, type).exclude(user_dt__date=date)

        if category == 'Ac':
            sum = queryset.aggregate(Sum('activity_duration'))['activity_duration__sum']
            if self.first_day:
                return sum
            else:
                return sum / self.nb_full_period_for_average(date, period)
        elif category == 'Su':
            count = queryset.count()
            if self.first_day:
                return count
            else:
                return count / self.nb_full_period_for_average(date, period)
        else:
            return None

    def filter_by_period(self, date, period, queryset):
        # filter by period
        if period == 'day':
            date_range = (
                datetime.datetime.combine(date, datetime.datetime.min.time().replace(tzinfo=pytz.UTC)),
                datetime.datetime.combine(date, datetime.datetime.max.time().replace(tzinfo=pytz.UTC))
            )
            return queryset.filter(user_dt__range=date_range)
        elif period == 'week':
            week_number = date.isocalendar()[1]
            return queryset.filter(user_dt__week=week_number)
        elif period == 'month':
            return queryset.filter(user_dt__month=date.month)

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
