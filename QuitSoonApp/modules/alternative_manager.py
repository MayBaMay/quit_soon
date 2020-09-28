#!/usr/bin/env python

"""
Module interacting with Alternative models
"""

from django.core.exceptions import ObjectDoesNotExist

from QuitSoonApp.models import Alternative, ConsoAlternative
from .manager import BaseManager


class AlternativeManager(BaseManager):
    """Manage informations of Alternative consumption"""

    def __init__(self, user, data):
        BaseManager.__init__(self, user, data)
        self.id_alternative = self.get_request_data('id_alternative')
        if not self.id_alternative:
            self.type_alternative = self.get_str(
                self.get_request_data('type_alternative')
                )
            self.type_activity = self.get_str(
                self.get_request_data('type_activity')
                )
            self.activity = self.get_str(
                self.get_request_data('activity')
                                                 )
            self.substitut = self.get_str(
                self.get_request_data('substitut')
                )
            self.nicotine = self.str_get_float(
                self.get_request_data('nicotine')
                )

    @staticmethod
    def get_str(data):
        """method return data formated as string"""
        if data == 'None' or not data:
            return None
        return str(data)

    @staticmethod
    def str_get_float(data):
        """method return string data as float"""
        if data == 'None' or not data:
            return None
        if isinstance(data, str):
            try:
                return float(data.replace(',','.'))
            except ValueError:
                return None
        return float(data)

    @property
    def get_alternative(self):
        """get Alternative instance with id or other data"""
        try:
            if self.id_alternative:
                alternative = Alternative.objects.get(id=self.id_alternative)
            else:
                alternative = Alternative.objects.get(
                    user=self.user,
                    type_alternative=self.type_alternative,
                    type_activity=self.type_activity,
                    activity=self.activity,
                    substitut=self.substitut,
                    nicotine=self.nicotine,
                    )
            return alternative
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    @property
    def filter_alternative(self):
        """filter Alternative with id or other data"""
        if self.id_alternative:
            alternative = Alternative.objects.filter(id=self.id_alternative)
        else:
            alternative = Alternative.objects.filter(
                user=self.user,
                type_alternative=self.type_alternative,
                type_activity=self.type_activity,
                activity=self.activity,
                substitut=self.substitut,
                nicotine=self.nicotine,
                )
        return alternative

    def create_alternative(self):
        """Create Alternative instance from data"""
        # unicity checked in form and in model index
        if self.get_alternative:
            new_alternative = self.filter_alternative
            new_alternative.update(display=True)
        else:
            new_alternative = Alternative.objects.create(
                user=self.user,
                type_alternative=self.type_alternative,
                type_activity=self.type_activity,
                activity=self.activity,
                substitut=self.substitut,
                nicotine=self.nicotine,
                )
        return new_alternative

    def delete_alternative(self):
        """delete Alternative instance with id"""
        if self.id_alternative:
            if self.get_alternative:
                alternative_filtered = self.filter_alternative
                # check if already smoked by user
                if ConsoAlternative.objects.filter(alternative=self.get_alternative):
                    # if yes: update display to False
                    alternative_filtered.update(display=False)
                else:
                    # if not: delete object
                    alternative_filtered.delete()
