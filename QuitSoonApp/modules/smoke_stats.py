#!/usr/bin/env python

from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from QuitSoonApp.models import UserProfile, Paquet, ConsoCig


class SmokeStats:
    """Generate stats reports on user smoke habits"""

    def __init__(self, user, lastday):
        self.user = user
        self.lastday = lastday
        self.date_start = UserProfile.objects.get(user=self.user).date_start
        self.nb_jour_since_start = (self.lastday - self.date_start).days + 1
        self.user_conso = ConsoCig.objects.filter(user=self.user)

    def nb_per_day(self, date):
        # nb smoke per day
        conso_day = self.user_conso.filter(date_cig=date)
        return conso_day.count()

    @property
    def total_smoke(self):
        return self.user_conso.count()

    @property
    def average_per_day(self):
        return self.total_smoke / self.nb_jour_since_start

    @property
    def count_smoking_day(self):
        smoking_days = ConsoCig.objects.order_by('date_cig').distinct('date_cig')
        return smoking_days.count()

    @property
    def count_no_smoking_day(self):
        return self.nb_jour_since_start - self.count_smoking_day

    @property
    def no_smoking_day(self):
        no_smoking_day = []
        start = datetime.combine(self.date_start, datetime.min.time())
        lastday = datetime.combine(self.lastday, datetime.min.time())
        delta =  lastday - start
        for i in range(delta.days + 1):
            day = start + timedelta(days=i)
            if not self.user_conso.filter(date_cig=day).exists():
                no_smoking_day.append(day.date())
        return no_smoking_day

    @property
    def total_money_smoked(self):
        money_smoked = 0
        for conso in self.user_conso:
            if conso.paquet:
                money_smoked += conso.paquet.price_per_cig
        return money_smoked

    @property
    def total_money_with_starting_nb_cig(self):
        money = 0
        #get first pack created
        starting_nb_cig = UserProfile.objects.get(user=self.user).starting_nb_cig
        first_pack = Paquet.objects.all()[0]
        money += self.nb_jour_since_start * first_pack.price_per_cig * starting_nb_cig
        return money

    @property
    def money_saved(self):
        return self.total_money_with_starting_nb_cig - self.total_money_smoked
