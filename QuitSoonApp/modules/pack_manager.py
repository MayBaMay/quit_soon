#!/usr/bin/env python

"""
This module allowes user to save a new instance of cigarettes pack
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from ..models import Paquet, ConsoCig

class PackManager:
    """class returning an new DB object paquet or False"""

    def __init__(self, user, datas):
        self.datas = datas
        self.user = user
        self.id = self.get_request_data('id_pack')
        if not self.id:
            self.type_cig = self.get_request_data('type_cig')
            self.brand = self.get_request_data('brand')
            self.qt_paquet = self.get_request_data('qt_paquet')
            self.unit = self.get_unit
            self.price = self.get_request_data('price')
            g_per_cig = self.get_request_data('g_per_cig')
            self.g_per_cig = self.get_g_per_cig(g_per_cig)
            self.price_per_cig = self.get_price_per_cig

    def get_request_data(self, data):
        try:
            return self.datas[data]
        except KeyError:
            return None

    @property
    def get_unit(self):
        """method getting unit from type_cig"""
        if self.type_cig in ['ROL', 'PIPE', 'GR']:
            return 'G'
        return 'U'

    def get_g_per_cig(self, g_per_cig=''):
        """ column g_per_cig only needed for """
        if g_per_cig:
            return g_per_cig
        else:
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

    @property
    def get_pack(self):
        try:
            if self.id:
                pack = Paquet.objects.get(id=self.id)
            else:
                pack = Paquet.objects.get(
                    user=self.user,
                    type_cig=self.type_cig,
                    brand=self.brand,
                    qt_paquet=self.qt_paquet,
                    price=self.price
                    )
            return pack
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None


    @property
    def filter_pack(self):
        if self.id:
            pack = Paquet.objects.filter(id=self.id)
        else:
            pack = Paquet.objects.filter(
                user=self.user,
                type_cig=self.type_cig,
                brand=self.brand,
                qt_paquet=self.qt_paquet,
                price=self.price
                )
        return pack

    def create_pack(self):
        """Create pack from datas"""
        if self.get_pack:
            newpack = self.filter_pack
            newpack.update(display=True)
        else:
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
        if self.id:
            if self.get_pack:
                pack_filtered = self.filter_pack
                # check if already smoked by user
                if ConsoCig.objects.filter(paquet=self.get_pack):
                    # if yes: update display to False
                    pack_filtered.update(display=False)
                else:
                    # if not: delete object
                    pack_filtered.delete()

    def update_pack_g_per_cig(self):
        try :
            pack_filtered = self.filter_pack
            pack_filtered.update(
                g_per_cig=self.g_per_cig,
                price_per_cig=self.get_price_per_cig
                )
        except ObjectDoesNotExist:
            pass
