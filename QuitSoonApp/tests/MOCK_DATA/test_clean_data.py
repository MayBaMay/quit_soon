#!/usr/bin/env python

"""Module testing smoke_stats module"""

from decimal import Decimal
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import Paquet, ConsoCig
from QuitSoonApp.modules import SmokeManager

from ..MOCK_DATA import Create_test_packs, Create_test_smoke


class CreateTestPacksTestCase(TestCase):
    """class testing Create_test_packs """

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.paquet_data = [
        {"type_cig":"ROL","brand":"Smelt","qt_paquet":30,"price":9.7, "display":False},
        {"type_cig":"IND","brand":"Enalapril Maleate","qt_paquet":10,"price":10, "display":True},
        ]
        self.packs = Create_test_packs(self.usertest, self.paquet_data)

    def test_get_missing_datas_pack(self):
        data = {"type_cig":"ROL","brand":"Smelt","qt_paquet":30,"price":9.7, "display":False}
        expected_data = {'type_cig': 'ROL', 'brand': 'Smelt', 'qt_paquet': 30, 'price': 9.7, 'display': False, 'unit': 'G', 'g_per_cig': 0.8, 'price_per_cig': Decimal('0.2586666666666666477188603797')}
        self.assertEqual(self.packs.get_missing_datas(data), expected_data)

    def test_populate_test_db(self):
        self.assertEqual(len(self.packs.clean_data), 2)
        self.packs.populate_test_db()
        self.assertEqual(Paquet.objects.count(), 2)
        self.assertEqual(Paquet.objects.get(id=1).brand, "Smelt")
        self.assertEqual(Paquet.objects.get(id=2).brand, "Enalapril Maleate")

class CreateTestSmokeTestCase(TestCase):
    """class testing Create_test_smoke """

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.paquet_data = [
        {"type_cig":"ROL","brand":"Smelt","qt_paquet":30,"price":9.7, "display":False},
        {"type_cig":"IND","brand":"Enalapril Maleate","qt_paquet":10,"price":10, "display":True},
        ]
        self.conso_cig_data = [
        {"date_cig":"2020-10-09","time_cig":"9:35","paquet":3,"given":True},
        {"date_cig":"2020-10-15","time_cig":"11:17","paquet":4}
        ]
        self.packs = Create_test_packs(self.usertest, self.paquet_data)
        self.packs.populate_test_db()
        self.smoke = Create_test_smoke(self.usertest, self.conso_cig_data)

    def test_get_missing_datas_smoke(self):
        self.assertEqual(len(self.packs.clean_data), 2)
        self.assertEqual(len(self.smoke.clean_data), 2)
        # given not specified, id ok
        data = {"date_cig":"2020-10-09","time_cig":"9:35","paquet":3}
        expected_data = {'date_cig': '2020-10-09', 'time_cig': '9:35', 'paquet': Paquet.objects.get(id=3), 'given': False}
        self.assertEqual(self.smoke.get_missing_datas(data), expected_data)
        # given False, ObjectDoesNotExist, random
        data = {"date_cig":"2020-10-09","time_cig":"9:35","paquet":100, 'given': False}
        clean_data = self.smoke.get_missing_datas(data)
        self.assertTrue(clean_data['paquet'] is not None)
        #call function twice
        self.assertEqual(self.smoke.get_missing_datas(data), clean_data)
        # given true
        data = {"date_cig":"2020-10-09","time_cig":"9:35","paquet":3, 'given': True}
        expected_data = {'date_cig': '2020-10-09', 'time_cig': '9:35', 'paquet': None, 'given': True}
        self.assertEqual(self.smoke.get_missing_datas(data), expected_data)

    def test_populate_test_db(self):
        self.smoke.populate_test_db()
        self.assertEqual(ConsoCig.objects.count(), 2)
        self.assertEqual(ConsoCig.objects.get(id=1).date_cig, datetime.date(2020, 10, 9))
        self.assertEqual(ConsoCig.objects.get(id=2).date_cig, datetime.date(2020, 10, 15))
