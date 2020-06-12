#!/usr/bin/env python

"""Module testing smoke_stats module"""

from decimal import Decimal
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import Paquet, ConsoCig
from QuitSoonApp.modules import SmokeManager

from ..MOCK_DATA import (
    Create_test_packs, Create_test_smoke,
    row_paquet_data, row_conso_cig_data
    )


class CreateTestPacksTestCase(TestCase):
    """class testing Create_test_packs """

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.paquet_data = row_paquet_data
        self.packs = Create_test_packs(self.usertest, self.paquet_data)

    def test_get_missing_datas_pack(self):
        data = {"type_cig":"ROL","brand":"Smelt","qt_paquet":30,"price":9.7, "display":False}
        expected_data = {'type_cig': 'ROL', 'brand': 'Smelt', 'qt_paquet': 30, 'price': 9.7, 'display': False, 'unit': 'G', 'g_per_cig': 0.8, 'price_per_cig': Decimal('0.2586666666666666477188603797')}
        self.assertEqual(self.packs.get_missing_datas(data), expected_data)

    def test_populate_test_db(self):
        self.assertEqual(len(self.packs.clean_data), 4)
        self.packs.populate_test_db()
        self.assertEqual(Paquet.objects.count(), 4)
        self.assertEqual(Paquet.objects.filter(brand='CAMEL').count(), 1)
        self.assertEqual(Paquet.objects.filter(brand='PHILIP MORIS').count(), 1)
        self.assertEqual(Paquet.objects.filter(brand='LUCKY STRIKE').count(), 1)
        self.assertEqual(Paquet.objects.filter(brand='1637').count(), 1)
        self.assertEqual(Paquet.objects.get(first=True).brand, 'CAMEL')

class CreateTestSmokeTestCase(TestCase):
    """class testing Create_test_smoke """

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.paquet_data = row_paquet_data
        self.conso_cig_data = row_conso_cig_data
        self.packs = Create_test_packs(self.usertest, self.paquet_data)
        self.packs.populate_test_db()
        self.smoke = Create_test_smoke(self.usertest, self.conso_cig_data)

    def test_get_missing_datas_smoke(self):
        self.assertEqual(len(self.packs.clean_data), 4)
        self.assertEqual(len(self.smoke.clean_data),329)
        # given not specified, id ok
        data = {"date_cig":"2020-10-09","time_cig":"9:35"}
        clean_data = self.smoke.get_missing_datas(data)
        self.assertEqual(clean_data['given'], False)
        self.assertTrue(clean_data['paquet'])
        # given False, ObjectDoesNotExist, random
        data = {"date_cig":"2020-10-09","time_cig":"9:35","paquet":100, 'given': False}
        clean_data = self.smoke.get_missing_datas(data)
        self.assertTrue(clean_data['paquet'] is not None)
        #call function twice
        self.assertEqual(self.smoke.get_missing_datas(data), clean_data)
        # given true
        data = {"date_cig":"2020-10-09","time_cig":"9:35", 'given': True}
        expected_data = {'date_cig': '2020-10-09', 'time_cig': '9:35', 'paquet': None, 'given': True}
        self.assertEqual(self.smoke.get_missing_datas(data), expected_data)

    def test_populate_test_db(self):
        self.smoke.populate_test_db()
        self.assertEqual(ConsoCig.objects.count(), 329)
