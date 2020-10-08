#!/usr/bin/env python

"""
Module interacting with ConsoAlternative models
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from QuitSoonApp.models import Alternative, ConsoAlternative
from .manager import ManagerConso


class HealthManager(ManagerConso):
    """Manage informations of healthy actions"""

    def __init__(self, user, data, tz_offset=0):
        ManagerConso.__init__(self, user, data)
        self.id_health = self.get_request_data('id_health')
        if not self.id_health:
            self.datetime_alter = self.get_datetime_client_aware(
                self.get_request_data('date_health'),
                self.get_request_data('time_health'),
                tz_offset
                )

    @property
    def get_conso_alternative(self):
        """get ConsoAlternative instance with id or other data"""
        try:
            if self.id_health:
                health = ConsoAlternative.objects.get(id=self.id_health)
            else:
                health = ConsoAlternative.objects.get(
                    user=self.user,
                    datetime_alter=self.datetime_alter,
                    alternative=self.get_alternative,
                    activity_duration=self.get_duration,
                    )
            return health
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    @property
    def get_alternative(self):
        """get Alternative instance with ConsoAlternative id or other data"""
        try:
            if self.id_health:
            # when user wants to delete a heath action,
            # ConsoAlternative.alternative is returned in request
                return self.get_conso_alternative.alternative
            type_alt = self.get_request_data('type_alternative_field')
            field = ''.join((type_alt.lower(), '_field'))
            id_alternative = self.get_request_data(field)
            return Alternative.objects.get(id=id_alternative)
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    @property
    def get_duration(self):
        """get duration activity in minutes"""
        try:
            duration_hour = self.get_request_data('duration_hour')
            duration_min = self.get_request_data('duration_min')
            return duration_hour * 60 + duration_min
        except TypeError:
            return None

    def create_conso_alternative(self):
        """Create ConsoAlternative from data"""
        try:
            newconsoalternative = ConsoAlternative.objects.create(
                user=self.user,
                datetime_alter=self.datetime_alter,
                alternative=self.get_alternative,
                activity_duration=self.get_duration,
                )
            self.id_health = newconsoalternative.id
            return newconsoalternative
        except (IntegrityError, AttributeError):
            return None

    def delete_conso_alternative(self):
        """delete ConsoAlternative instance with id"""
        try:
            if self.id_health:
                self.get_conso_alternative.delete()
        except AttributeError:
            pass
