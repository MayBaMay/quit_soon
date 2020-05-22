#!/usr/bin/env python

"""
This module allowes user to save a new instance of cigarettes pack
"""
from decimal import *

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from ..models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)

class SaveAlternative:
    """class returning an new DB object paquet or False"""

    def __init__(self, user, datas):
        self.user = user
        self.type_alternative = self.if_strNone_get_None_or_str(datas['type_alternative'])
        try:
            self.type_activity = self.if_strNone_get_None_or_str(datas['type_activity'])
        except KeyError:
            self.type_activity = None
        try:
            self.activity = self.if_strNone_get_None_or_str(datas['activity'])
        except KeyError:
            self.activity = None
        try:
            self.substitut = self.if_strNone_get_None_or_str(datas['substitut'])
        except KeyError:
            self.substitut = None
        try:
            self.nicotine = self.if_strNone_get_None_or_float(datas['nicotine'])
        except KeyError:
            self.nicotine = None

    @staticmethod
    def if_strNone_get_None_or_str(data):
        if data == 'None':
            return None
        return str(data)

    @staticmethod
    def if_strNone_get_None_or_float(data):
        if type(data) == str:
            if data == 'None':
                return None
            else:
                try:
                    return float(data.replace(',','.'))
                except ValueError:
                    return None
        else:
            return float(data)

    def create_alternative(self):
        """Create pack from datas"""
        # unicity checked in form and in model index
        try:
            self.get_alternative
            alternative = self.filter_alternative
            alternative.update(display=True)
        except:
            newAlternative = Alternative.objects.create(
                user=self.user,
                type_alternative=self.type_alternative,
                type_activity=self.type_activity,
                activity=self.activity,
                substitut=self.substitut,
                nicotine=self.nicotine,
                )
            return newAlternative

    @property
    def get_alternative(self):
        alternative = Alternative.objects.get(
            user=self.user,
            type_alternative=self.type_alternative,
            type_activity=self.type_activity,
            activity=self.activity,
            substitut=self.substitut,
            nicotine=self.nicotine,
            )
        return alternative

    @property
    def filter_alternative(self):
        alternative = Alternative.objects.filter(
            user=self.user,
            type_alternative=self.type_alternative,
            type_activity=self.type_activity,
            activity=self.activity,
            substitut=self.substitut,
            nicotine=self.nicotine,
            )
        return alternative

    def delete_alternative(self):
        try :
            alternative = self.get_alternative
            alternative_filtered = self.filter_alternative
            # check if already smoked by user
            if ConsoAlternative.objects.filter(alternative=alternative):
                # if yes: update display to False
                alternative_filtered.update(display=False)
            else:
                # if not: delete object
                alternative_filtered.delete()
        except ObjectDoesNotExist as e:
            print(e)

#     # def update_pack_g_per_cig(self):
#     #     try :
#     #         pack_filtered = Paquet.objects.filter(
#     #             user=self.user,
#     #             type_cig=self.type_cig,
#     #             brand=self.brand,
#     #             qt_paquet=self.qt_paquet,
#     #             price=self.price
#     #             )
#     #         pack_filtered.update(g_per_cig=self.g_per_cig)
#     #     except ObjectDoesNotExist:
#     #         pass
