#!/usr/bin/env python

"""
This module allowes user to save a new instance of cigarettes pack
"""
from django.contrib.auth.models import User
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
        self.brand = datas['brand'].upper()
        self.qt_paquet = datas['qt_paquet']
        self.unit = self.get_unit()
        self.price = datas['price']
        self.g_per_cig = self.get_g_per_cig()

    def get_unit(self):
        """method getting unit from type_cig"""
        if self.type_cig in ['ROL', 'PIPE', 'GR']:
            return 'G'
        return 'U'

    def get_g_per_cig(self):
        """ column g_per_cig only needed for """
        if self.unit == 'G':
            return 0.8
        return None

    def create_pack(self):
        """Create pack from datas"""
        newpack = Paquet.objects.create(
            user=self.user,
            type_cig=self.type_cig,
            brand=self.brand,
            qt_paquet=self.qt_paquet,
            unit=self.unit,
            price=self.price,
            g_per_cig=self.g_per_cig,
            )
        return newpack
