#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)


"""Module testing clean_data module cleaning row_data for tests"""

from decimal import Decimal
import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from QuitSoonApp.models import Paquet, ConsoCig, Alternative, ConsoAlternative

from ..MOCK_DATA import (
    CreatePacks, CreateSmoke,
    CreateAlternative, CreateConsoAlternative,
    row_paquet_data, row_conso_cig_data,
    row_alternative_data, row_conso_alt_data,
    )


class CreateTestPacksTestCase(TestCase):
    """class testing CreatePacks for tests """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'Newuser', 'test@test.com', 'testpassword'
            )
        self.paquet_data = row_paquet_data
        self.packs = CreatePacks(self.user, self.paquet_data)

    def test_get_missing_data_pack(self):
        """test method get_missing_data for Paquet data"""
        data = {
            "type_cig":"ROL",
            "brand":"Smelt",
            "qt_paquet":30,
            "price":9.7,
            "display":False
            }
        expected_data = {
            'type_cig': 'ROL',
            'brand': 'Smelt',
            'qt_paquet': 30,
            'price': 9.7,
            'display': False,
            'unit': 'G',
            'g_per_cig': 0.8,
            'price_per_cig': Decimal('0.2586666666666666477188603797')
            }
        self.assertEqual(self.packs.get_missing_data(data), expected_data)

    def test_populate_db(self):
        """test method populate_db"""
        self.assertEqual(len(self.packs.clean_data), 4)
        self.packs.populate_db()
        self.assertEqual(Paquet.objects.count(), 4)
        self.assertEqual(Paquet.objects.filter(brand='CAMEL').count(), 1)
        self.assertEqual(Paquet.objects.filter(brand='PHILIP MORIS').count(), 1)
        self.assertEqual(Paquet.objects.filter(brand='LUCKY STRIKE').count(), 1)
        self.assertEqual(Paquet.objects.filter(brand='1637').count(), 1)
        self.assertEqual(Paquet.objects.get(first=True).brand, 'CAMEL')

class CreateTestSmokeTestCase(TestCase):
    """class testing CreateSmoke for tests """
    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'Newuser', 'test@test.com', 'testpassword'
            )
        self.paquet_data = row_paquet_data
        self.conso_cig_data = row_conso_cig_data
        self.packs = CreatePacks(self.user, self.paquet_data)
        self.packs.populate_db()
        self.smoke = CreateSmoke(self.user, self.conso_cig_data)

    def test_get_missing_data_smoke(self):
        """test method get_missing_data for ConsoCig data"""
        self.assertEqual(len(self.packs.clean_data), 4)
        self.assertEqual(len(self.smoke.clean_data),329)
        # given not specified, id ok
        data = {"date_cig":"2020-10-09","time_cig":"9:35", "paquet":1001}
        clean_data = self.smoke.get_missing_data(data)
        self.assertEqual(clean_data['given'], False)
        self.assertTrue(clean_data['paquet'])
        # given False, ObjectDoesNotExist, random
        data = {
            "date_cig":"2020-10-09",
            "time_cig":"9:35",
            "paquet":1001,
            'given': False
            }
        clean_data = self.smoke.get_missing_data(data)
        self.assertTrue(clean_data['paquet'] is not None)
        #call function twice
        self.assertEqual(self.smoke.get_missing_data(data), clean_data)
        # given true
        data = {"date_cig":"2020-10-09","time_cig":"9:35", 'given': True}
        expected_data = {
            'date_cig': '2020-10-09',
            'time_cig': '9:35',
            'paquet': None,
            'given': True
            }
        self.assertEqual(self.smoke.get_missing_data(data), expected_data)

    def test_populate_db(self):
        """test method populate_db"""
        self.smoke.populate_db()
        self.assertEqual(ConsoCig.objects.count(), 329)
        self.assertEqual(ConsoCig.objects.all()[0].datetime_cig, make_aware(
            datetime.datetime(2019, 9, 28, 9, 0), pytz.utc))
        self.assertEqual(
            ConsoCig.objects.all()[0].paquet, Paquet.objects.get(id=1001))
        self.assertEqual(ConsoCig.objects.all()[0].given, False)


class CreateAlternativeTestCase(TestCase):
    """class testing CreateAlternative for tests """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'Newuser', 'test@test.com', 'testpassword'
            )
        self.alternative_data = row_alternative_data
        self.alternatives = CreateAlternative(self.user, self.alternative_data)

    def test_get_missing_data(self):
        """test method populate_db for Alternative data"""
        data = {
            "type_alternatives":"Ac",
            "type_activity":"Sp",
            "activity":"COURSE",
            "id":1001
            }
        expected_data = {
            "type_alternatives":"Ac",
            "type_activity":"Sp",
            "activity":"COURSE",
            "substitut":None,
            "nicotine":None,
            "id":1001
            }
        self.assertEqual(self.alternatives.get_missing_data(data), expected_data)

    def test_populate_db(self):
        """test method populate_db"""
        self.assertEqual(len(self.alternatives.clean_data), 5)
        self.alternatives.populate_db()
        self.assertEqual(Alternative.objects.count(), 5)
        self.assertEqual(Alternative.objects.filter(type_activity='Sp').count(), 1)
        self.assertEqual(Alternative.objects.filter(type_activity='Lo').count(), 1)
        self.assertEqual(Alternative.objects.filter(type_activity='So').count(), 1)
        self.assertEqual(Alternative.objects.filter(substitut='P').count(), 1)
        self.assertEqual(Alternative.objects.filter(substitut='PAST').count(), 1)


class CreateConsoAlternativeTestCase(TestCase):
    """class testing CreateConsoAlternative for tests """
    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'Newuser', 'test@test.com', 'testpassword'
            )
        self.alternatives = CreateAlternative(self.user, row_alternative_data)
        self.alternatives.populate_db()
        self.health = CreateConsoAlternative(self.user, row_conso_alt_data)

    def test_get_missing_data_smoke(self):
        """test method get_missing_data for ConsoCig data"""
        self.assertEqual(len(self.alternatives.clean_data), 5)
        self.assertEqual(len(self.health.clean_data),58)
        # data substitut
        data = {
            'date_alter': '2019-09-28',
            'time_alter': '20:20',
            'alternative': 1005
            }
        alternative = Alternative.objects.get(id=1005)
        expected_data = {
            'date_alter': '2019-09-28',
            'time_alter': '20:20',
            'alternative': alternative,
            'activity_duration': None
            }
        clean_data = self.health.get_missing_data(data)
        self.assertEqual(clean_data['activity_duration'], None)
        self.assertEqual(clean_data['alternative'], alternative)
        self.assertEqual(clean_data, expected_data)
        # data activity
        data = {
            'date_alter': '2019-09-28',
            'time_alter': '20:20',
            'alternative': 1002,
            'activity_duration': 45
            }
        alternative = Alternative.objects.get(id=1002)
        expected_data = {
            'date_alter': '2019-09-28',
            'time_alter': '20:20',
            'alternative': alternative,
            'activity_duration': 45
            }
        clean_data = self.health.get_missing_data(data)
        self.assertEqual(clean_data['activity_duration'], 45)
        self.assertEqual(clean_data['alternative'], alternative)
        self.assertEqual(clean_data, expected_data)

    def test_populate_db(self):
        """test method populate_db for ConsoAlternative data"""
        self.health.populate_db()
        self.assertEqual(ConsoAlternative.objects.count(), 58)
