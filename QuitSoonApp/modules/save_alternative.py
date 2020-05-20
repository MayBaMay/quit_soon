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
        self.type_alternative = datas['type_alternative']
        self.alternative = datas['alternative']
        self.nicotine = datas['nicotine']

    def create_alternative(self):
        """Create pack from datas"""
        # unicity checked in form and in model index
        newAlternative = Alternative.objects.create(
            user=self.user,
            type_alternative=self.type_alternative,
            alternative=self.alternative,
            nicotine=self.nicotine,
            )
        return newAlternative

    # def delete_pack(self):
    #     try :
    #         pack = Paquet.objects.get(
    #             user=self.user,
    #             type_cig=self.type_cig,
    #             brand=self.brand,
    #             qt_paquet=self.qt_paquet,
    #             price=self.price
    #             )
    #         pack_filtered = Paquet.objects.filter(
    #             user=self.user,
    #             type_cig=self.type_cig,
    #             brand=self.brand,
    #             qt_paquet=self.qt_paquet,
    #             price=self.price
    #             )
    #         # check if already smoked by user
    #         if ConsoCig.objects.filter(paquet=pack):
    #             # if yes: update display to False
    #             pack_filtered.update(display=False)
    #         else:
    #             # if not: delete object
    #             pack_filtered.delete()
    #     except ObjectDoesNotExist:
    #         pass
    #
    # def update_pack_g_per_cig(self):
    #     try :
    #         pack_filtered = Paquet.objects.filter(
    #             user=self.user,
    #             type_cig=self.type_cig,
    #             brand=self.brand,
    #             qt_paquet=self.qt_paquet,
    #             price=self.price
    #             )
    #         pack_filtered.update(g_per_cig=self.g_per_cig)
    #     except ObjectDoesNotExist:
    #         pass
