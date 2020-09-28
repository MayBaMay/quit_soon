#!/usr/bin/env python

"""
Module interacting with Paquet models
"""

from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist

from ..models import Paquet, ConsoCig
from .manager import BaseManager

class PackManager(BaseManager):
    """Manage informations of user packs"""

    def __init__(self, user, data):
        BaseManager.__init__(self, user, data)
        self.id_pack = self.get_request_data('id_pack')
        if not self.id_pack:
            self.first = False
            if not Paquet.objects.filter(user=self.user).exists():
                self.first =  True
            self.type_cig = self.get_request_data('type_cig')
            self.brand = self.get_request_data('brand')
            self.qt_paquet = self.get_request_data('qt_paquet')
            self.price = self.get_request_data('price')

    @property
    def unit(self):
        """method getting unit from type_cig"""
        if self.type_cig in ['ROL', 'PIPE', 'GR']:
            return 'G'
        return 'U'

    @property
    def g_per_cig(self):
        """ column g_per_cig only needed for """
        g_per_cig = self.get_request_data('g_per_cig')
        if g_per_cig:
            return g_per_cig
        if self.unit == 'G':
            return 0.8
        return None

    @property
    def price_per_cig(self):
        """ get price per cigarette """
        if self.unit == 'G':
            nb_cig = self.qt_paquet / self.g_per_cig
            return Decimal(self.price) / Decimal(nb_cig)
        return Decimal(self.price)/self.qt_paquet

    @property
    def get_pack(self):
        """get Paquet object from attributs"""
        try:
            if self.id_pack:
                pack = Paquet.objects.get(id=self.id_pack)
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
        """filter Paquet object from attributs"""
        if self.id_pack:
            pack = Paquet.objects.filter(id=self.id_pack)
        else:
            pack = Paquet.objects.filter(
                user=self.user,
                type_cig=self.type_cig,
                brand=self.brand,
                qt_paquet=self.qt_paquet,
                price=self.price
                )
        return pack

    def init_first(self):
        """method setting pack's as reference pack (col first)"""
        # make sure all the other user packs are not set as first
        Paquet.objects.filter(user=self.user).update(first=False)
        self.first =  True

    def create_pack(self):
        """Create pack from data"""
        if self.get_pack:
            self.filter_pack.update(display=True, first=self.first)
            newpack = self.get_pack
        else:
            newpack = Paquet.objects.create(
                user=self.user,
                type_cig=self.type_cig,
                brand=self.brand,
                qt_paquet=self.qt_paquet,
                unit=self.unit,
                price=self.price,
                g_per_cig=self.g_per_cig,
                price_per_cig=self.price_per_cig,
                first=self.first,
                )
        return newpack

    def delete_pack(self):
        """delete pack"""
        if self.id_pack:
            if self.get_pack:
                pack_filtered = self.filter_pack
                # check if already smoked by user
                if ConsoCig.objects.filter(paquet=self.get_pack) or self.get_pack.first:
                    # if yes: update display to False
                    pack_filtered.update(display=False)
                else:
                    # if not: delete object
                    pack_filtered.delete()

    def update_pack_g_per_cig(self):
        """update g_per_cig paquet info"""
        pack_filtered = self.filter_pack
        pack_filtered.update(
            g_per_cig=self.g_per_cig,
            price_per_cig=self.price_per_cig
            )
