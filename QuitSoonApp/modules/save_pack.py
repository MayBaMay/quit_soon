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

class SavePack:
    """class returning an new DB object paquet or False"""

    def __init__(self, user, datas):
        self.user = user
        self.type_cig = datas['type_cig']
        self.brand = datas['brand']
        self.qt_paquet = datas['qt_paquet']
        self.unit = self.get_unit
        self.price = datas['price']
        self.g_per_cig = self.get_initial_g_per_cig
        self.price_per_cig = self.get_price_per_cig

    @property
    def get_unit(self):
        """method getting unit from type_cig"""
        if self.type_cig in ['ROL', 'PIPE', 'GR']:
            return 'G'
        return 'U'

    @property
    def get_initial_g_per_cig(self):
        """ column g_per_cig only needed for """
        if self.unit == 'G':
            return 0.8
        return None

    @property
    def get_price_per_cig(self):
        """ get price per cigarette """
        if self.unit == 'G':
            nb_cig = self.qt_paquet / self.g_per_cig
            return Decimal(self.price) / Decimal(nb_cig)
        return Decimal(self.price)/self.qt_paquet

    def create_pack(self):
        """Create pack from datas"""
        # unicity checked in form and in model index
        newpack = Paquet.objects.create(
            user=self.user,
            type_cig=self.type_cig,
            brand=self.brand,
            qt_paquet=self.qt_paquet,
            unit=self.unit,
            price=self.price,
            g_per_cig=self.g_per_cig,
            price_per_cig=self.price_per_cig
            )
        return newpack

    def delete_pack(self):
        try :
            pack = Paquet.objects.get(
                user=self.user,
                type_cig=self.type_cig,
                brand=self.brand,
                qt_paquet=self.qt_paquet,
                price=self.price
                )
            pack_filtered = Paquet.objects.filter(
                user=self.user,
                type_cig=self.type_cig,
                brand=self.brand,
                qt_paquet=self.qt_paquet,
                price=self.price
                )
            # check if already smoked by user
            if ConsoCig.objects.filter(paquet=pack):
                # if yes: update display to False
                pack_filtered.update(display=False)
            else:
                # if not: delete object
                pack_filtered.delete()
        except ObjectDoesNotExist:
            pass
