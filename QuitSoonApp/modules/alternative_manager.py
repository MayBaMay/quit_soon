#!/usr/bin/env python

"""
This module allowes user to save a new instance of cigarettes pack
"""

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from ..models import Alternative, ConsoAlternative

class AlternativeManager:
    """class returning an new DB object paquet or False"""

    def __init__(self, user, datas):
        self.user = user
        self.datas = datas
        self.id = self.get_request_data('id_alternative')
        if not self.id:
            self.type_alternative = self.if_strNone_get_None_or_str(self.get_request_data('type_alternative'))
            self.type_activity = self.if_strNone_get_None_or_str(self.get_request_data('type_activity'))
            self.activity = self.if_strNone_get_None_or_str(self.get_request_data('activity'))
            self.substitut = self.if_strNone_get_None_or_str(self.get_request_data('substitut'))
            self.nicotine = self.if_strNone_get_None_or_float(self.get_request_data('nicotine'))

    def get_request_data(self, data):
        try:
            return self.datas[data]
        except KeyError:
            return None


    @staticmethod
    def if_strNone_get_None_or_str(data):
        if data == 'None' or data == None:
            return None
        return str(data)

    @staticmethod
    def if_strNone_get_None_or_float(data):
        if data == 'None' or data == None:
            return None
        else:
            if type(data) == str:
                try:
                    return float(data.replace(',','.'))
                except ValueError:
                    return None
            else:
                return float(data)

    @property
    def get_alternative(self):
        try:
            if self.id:
                alternative = Alternative.objects.get(id=self.id)
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
        if self.id:
            alternative = Alternative.objects.filter(id=self.id)
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
        """Create pack from datas"""
        # unicity checked in form and in model index
        if self.get_alternative:
            newAlternative = self.filter_alternative
            newAlternative.update(display=True)
        else:
            newAlternative = Alternative.objects.create(
                user=self.user,
                type_alternative=self.type_alternative,
                type_activity=self.type_activity,
                activity=self.activity,
                substitut=self.substitut,
                nicotine=self.nicotine,
                )
        return newAlternative

    def delete_alternative(self):
        if self.id:
            if self.get_alternative:
                alternative_filtered = self.filter_alternative
                # check if already smoked by user
                if ConsoAlternative.objects.filter(alternative=self.get_alternative):
                    # if yes: update display to False
                    alternative_filtered.update(display=False)
                else:
                    # if not: delete object
                    alternative_filtered.delete()
