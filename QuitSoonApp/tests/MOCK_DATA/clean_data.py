#!/usr/bin/env python

from decimal import Decimal
from random import randint

from django.core.exceptions import ObjectDoesNotExist

from QuitSoonApp.models import Paquet, ConsoCig

class Create_test_packs:

    def __init__(self, user, paquet_data):
        self.user = user
        self.clean_data = paquet_data
        for data in self.clean_data:
            data = self.get_missing_datas(data)

    def get_missing_datas(self, data):
        # unit, g_per_cig, price_per_cig
        if data['type_cig'] == 'ROL':
            data['unit'] = 'G'
            data['g_per_cig'] = 0.8
            nb_cig = data['qt_paquet'] / data['g_per_cig']
            data['price_per_cig'] =  Decimal(data['price']) / Decimal(nb_cig)
            return data
        else:
            data['unit'] = 'U'
            data['g_per_cig'] = None
            data['price_per_cig'] = Decimal(data['price'])/data['qt_paquet']
            return data

    def populate_test_db(self):
        for data in self.clean_data:
            Paquet.objects.create(
                user=self.user,
                type_cig=data['type_cig'],
                brand=data['brand'],
                qt_paquet=data['qt_paquet'],
                unit=data['unit'],
                price=data['price'],
                g_per_cig=data['g_per_cig'],
                price_per_cig=data['price_per_cig'],
                display=data['display'],
                )

class Create_test_smoke:

    def __init__(self, user, conso_cig_data):
        self.user = user
        self.clean_data = conso_cig_data
        for data in self.clean_data:
            data = self.get_missing_datas(data)

    def get_missing_datas(self, data):
        try:
            if data['given'] == True:
                data['paquet'] = None
            else:
                data = self.get_pack(data)
        except KeyError:
            # data['given'] not specified so default False
            data = self.get_pack(data)
        return data

    @staticmethod
    def get_pack(data):
        data['given'] = False
        try:
            pack = Paquet.objects.get(id=data['paquet'])
            data['paquet'] = pack
        except (ObjectDoesNotExist, KeyError, TypeError):
            # id not in Paquet's ids or not indicated or function called twice, paquet already filled
            ids = []
            for pack in Paquet.objects.all():
                ids.append(pack.id)
            id = randint(ids[0], ids[-1])
            pack = Paquet.objects.get(id=id)
            data['paquet'] = pack
        return data

    def populate_test_db(self):
        for data in self.clean_data:
            ConsoCig.objects.create(
                user=self.user,
                date_cig=data['date_cig'],
                time_cig=data['time_cig'],
                paquet=data['paquet'],
                given=data['given'],
                )
