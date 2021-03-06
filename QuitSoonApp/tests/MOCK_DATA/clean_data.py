#!/usr/bin/env python
# pylint: disable=duplicate-code
# pylint: disable=duplicate-code


"""
Clean tests data and populate test database
"""

from decimal import Decimal
from datetime import datetime as dt
import pytz

from QuitSoonApp.models import Paquet, ConsoCig, Alternative, ConsoAlternative


class CreateDataInDatabase:
    """
    Class with common methods and attributes
    to parse, complete and use data to populate tables in testing database
    """

    def __init__(self, user, row_data):
        self.user = user
        self.clean_data = row_data

    @staticmethod
    def date_format(date):
        """formate date into string"""
        return dt.strptime(date, '%Y-%m-%d').date()

    @staticmethod
    def time_format(time):
        """formate time into string"""
        return dt.strptime(time, '%H:%M').time()


class CreatePacks(CreateDataInDatabase):
    """Parse, complete and use data to populate table Paquet in test database"""

    def __init__(self, user, row_data):
        super().__init__(user, row_data)
        for data in self.clean_data:
            data = self.get_missing_data(data)

    @staticmethod
    def get_missing_data(data):
        """complete row_data with expected info"""
        # unit, g_per_cig, price_per_cig
        if data['type_cig'] == 'ROL':
            data['unit'] = 'G'
            data['g_per_cig'] = 0.8
            nb_cig = data['qt_paquet'] / data['g_per_cig']
            data['price_per_cig'] =  Decimal(data['price']) / Decimal(nb_cig)
            return data
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

class CreateSmoke(CreateDataInDatabase):
    """Parse, complete and use data to populate table ConsoCig in test database"""

    def __init__(self, user, row_data):
        super().__init__(user, row_data)
        for data in self.clean_data:
            data = self.get_missing_data(data)

    def get_missing_data(self, data):
        """complete row_data with expected info"""
        try:
            if data['given']:
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
        """get Paquet instance with id"""
        data['given'] = False
        try:
            pack = Paquet.objects.get(id=data['paquet'])
            data['paquet'] = pack
        except TypeError:
            pass
        return data

    def populate_db(self):
        """Populate database with tests ConsoCig"""
        for data in self.clean_data:
            date = self.date_format(data['date_cig'])
            time = self.time_format(data['time_cig']).replace(tzinfo=pytz.UTC)
            datetime_cig = dt.combine(date, time)
            ConsoCig.objects.create(
                user=self.user,
                datetime_cig=datetime_cig,
                paquet=data['paquet'],
                given=data['given'],
                )

class CreateAlternative(CreateDataInDatabase):
    """Parse, complete and use data to populate table Alternative in test database"""

    def __init__(self, user, row_data):
        super().__init__(user, row_data)
        for data in self.clean_data:
            data = self.get_missing_data(data)

    @staticmethod
    def get_missing_data(data):
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
        """Populate database with tests Alternative """
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

    def __init__(self, user, row_data):
        super().__init__(user, row_data)
        for data in self.clean_data:
            data = self.get_missing_data(data)

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
        """get Alternative instance with id"""
        try:
            alt = Alternative.objects.get(id=data['alternative'])
            data['alternative'] = alt
        except TypeError:
            pass
        return data['alternative']

    def populate_db(self):
        """Populate database with test ConsoAlternative"""
        for data in self.clean_data:
            date = self.date_format(data['date_alter'])
            time = self.time_format(data['time_alter']).replace(tzinfo=pytz.UTC)
            datetime_alter = dt.combine(date, time)
            ConsoAlternative.objects.create(
                user=self.user,
                datetime_alter=datetime_alter,
                alternative=data['alternative'],
                activity_duration=data['activity_duration'],
                )
