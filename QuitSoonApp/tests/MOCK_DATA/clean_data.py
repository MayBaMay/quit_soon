#!/usr/bin/env python

"""
Clean tests data and populate test database
"""

from datetime import datetime as dt
from decimal import Decimal
from random import randint

from django.core.exceptions import ObjectDoesNotExist

from QuitSoonApp.models import Paquet, ConsoCig, Alternative, ConsoAlternative


class CreateDataInDatabase:

    def __init__(self, user, row_data):
        self.user = user
        self.clean_data = row_data
        for data in self.clean_data:
            data = self.get_missing_data(data)

    def date_format(self, date):
        return dt.strptime(date, '%Y-%M-%d').date()

    def time_format(self, time):
        return dt.strptime(time, '%H:%M').time()


class Create_packs(CreateDataInDatabase):
    """Parse, complete and use data to populate table Paquet in test database"""

    def get_missing_data(self, data):
        """complete row_data with expected info"""
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

    def populate_db(self):
        """populate database with clean data"""
        for data in self.clean_data:
            Paquet.objects.create(
                id=data['id'],
                user=self.user,
                type_cig=data['type_cig'],
                brand=data['brand'],
                qt_paquet=data['qt_paquet'],
                unit=data['unit'],
                price=data['price'],
                g_per_cig=data['g_per_cig'],
                price_per_cig=data['price_per_cig'],
                display=data['display'],
                first=data['first']
                )

class Create_smoke(CreateDataInDatabase):
    """Parse, complete and use data to populate table ConsoCig in test database"""

    def get_missing_data(self, data):
        """complete row_data with expected info"""
        try:
            if data['given'] == True:
                data['paquet'] = None
            else:
                # => data['given'] = False
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
        except TypeError: #(ObjectDoesNotExist, KeyError, ):
            # function called twice(paquet already filled)
            pass
        return data

    def populate_db(self):
        for data in self.clean_data:
            conso = ConsoCig.objects.create(
                user=self.user,
                date_cig=self.date_format(data['date_cig']),
                time_cig=self.time_format(data['time_cig']),
                paquet=data['paquet'],
                given=data['given'],
                )

class CreateAlternative(CreateDataInDatabase):
    """Parse, complete and use data to populate table Alternative in test database"""

    def get_missing_data(self, data):
        """complete row_data with expected info"""
        try:
            if data['type_activity']:
                data['substitut'] = None
                data['nicotine'] = None
        except KeyError:
            data['type_activity'] = None
            data['activity'] = None
        return data

    def populate_db(self):
        for data in self.clean_data:
            Alternative.objects.create(
                id=data['id'],
                user=self.user,
                type_alternative=data['type_alternative'],
                type_activity=data['type_activity'],
                activity=data['activity'],
                substitut=data['substitut'],
                nicotine=data['nicotine'],
                )


class CreateConsoAlternative(CreateDataInDatabase):
    """Parse, complete and use data to populate table ConsoCig in test database"""

    def get_missing_data(self, data):
        """complete row_data with expected info"""
        try:
            data['activity_duration']
        except KeyError:
            data['activity_duration'] = None
        data['alternative'] = self.get_alternative(data)
        return data

    @staticmethod
    def get_alternative(data):
        try:
            alt = Alternative.objects.get(id=data['alternative'])
            data['alternative'] = alt
        except TypeError: #(ObjectDoesNotExist, KeyError, ):
            # function called twice(paquet already filled)
            pass
        return data['alternative']

    def populate_db(self):
        for data in self.clean_data:
            ConsoAlternative.objects.create(
                user=self.user,
                date_alter=self.date_format(data['date_alter']),
                time_alter=self.time_format(data['time_alter']),
                alternative=data['alternative'],
                activity_duration=data['activity_duration'],
                )
