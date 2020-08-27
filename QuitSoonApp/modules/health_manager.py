#!/usr/bin/env python

import datetime
from datetime import timedelta
import pytz

from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from QuitSoonApp.models import Alternative, ConsoAlternative


class HealthManager:
    """Manage informations of healthy actions"""

    def __init__(self, user, datas, tz_offset=0):
        self.datas = datas
        self.user = user
        self.id = self.get_request_data('id_health')
        if not self.id:
            self.datetime_alter = self.get_datetime_alter_aware(
                self.get_request_data('date_health'),
                self.get_request_data('time_health'),
                tz_offset
                )
            self.date_alter = self.datetime_alter.date()
            self.time_alter = self.datetime_alter.time()


    def get_datetime_alter_aware(self, date_health, time_health, tz_offset):
        try:
            dt_alter = datetime.datetime.combine(date_health, time_health)
            dt_alter += timedelta(minutes=tz_offset)
            dt_alter = make_aware(dt_alter, pytz.utc)
            return dt_alter
        except TypeError:
            # get_request_data returned None
            return None

    def get_request_data(self, data):
        try:
            return self.datas[data]
        except (KeyError, TypeError):
            return None

    @property
    def get_conso_alternative(self):
        try:
            if self.id:
                health = ConsoAlternative.objects.get(id=self.id)
            else:
                health = ConsoAlternative.objects.get(
                    user=self.user,
                    date_alter=self.date_alter,
                    time_alter=self.time_alter,
                    datetime_alter=self.datetime_alter,
                    alternative=self.get_alternative,
                    activity_duration=self.get_duration,
                    ecig_choice=self.get_ecig_data,
                    )
            return health
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    @property
    def get_alternative(self):
        try:
            if self.id:
            # when user wants to delete a heath action, ConsoAlternative.alternative is returned in request
                return self.get_conso_alternative.alternative
            else:
                type = self.get_request_data('type_alternative_field')
                field = ''.join((type.lower(), '_field'))
                id_alternative = self.get_request_data(field)
                return Alternative.objects.get(id=id_alternative)
        except (ObjectDoesNotExist, ValueError, AttributeError):
                return None

    @property
    def get_duration(self):
        try:
            hour = self.get_request_data('duration_hour')
            min = self.get_request_data('duration_min')
            return hour*60 + min
        except TypeError:
            return None

    @property
    def get_ecig_data(self):
        ecig_choice = self.get_request_data('ecig_vape_or_start')
        if ecig_choice == [] or not ecig_choice :
            return None
        elif ecig_choice == ['V'] or ecig_choice == ['S']:
            return ecig_choice[0]
        elif ecig_choice == ['V', 'S'] or ecig_choice == ['S', 'V']:
            return 'VS'

    def create_conso_alternative(self):
        """Create ConsoAlternative from datas"""
        try:
            newconsoalternative = ConsoAlternative.objects.create(
                user=self.user,
                date_alter=self.date_alter,
                time_alter=self.time_alter,
                datetime_alter=self.datetime_alter,
                alternative=self.get_alternative,
                activity_duration=self.get_duration,
                ecig_choice=self.get_ecig_data,
                )
            self.id = newconsoalternative.id
            return newconsoalternative
        except (IntegrityError, AttributeError):
            return None

    def delete_conso_alternative(self):
        try:
            if self.id:
                self.get_conso_alternative.delete()
        except AttributeError:
            pass
