#!/usr/bin/env python

"""Module testing health user action manager module"""

import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import Alternative, ConsoAlternative
from QuitSoonApp.modules import HealthManager


class HealthManagerTestCase(TestCase):
    """class testing HealthManager """

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.alternative_sp = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            )
        self.alternative_so = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='TABACOLOGUE',
            )
        self.alternative_su = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='P24',
            nicotine=2,
            )
        self.alternative_su_ecig = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='ECIG',
            nicotine=6,
            )
        self.data_sp = {
            'date_health': datetime.date(2020, 5, 17),
            'time_health': datetime.time(13, 15),
            'type_alternative_field':'Sp',
            'sp_field': self.alternative_sp.id,
            'so_field': self.alternative_so.id,
            'su_field':self.alternative_su.id,
            'duration_hour':1,
            'duration_min':30,
            }
        self.data_su = {
            'date_health': datetime.date(2020, 5, 17),
            'time_health': datetime.time(14, 15),
            'type_alternative_field':'Su',
            'sp_field': self.alternative_sp.id,
            'so_field': self.alternative_so.id,
            'su_field':self.alternative_su.id,
            }
        self.data_su_ecig = {
            'date_health': datetime.date(2020, 5, 17),
            'time_health': datetime.time(14, 15),
            'type_alternative_field':'Su',
            'sp_field': self.alternative_sp.id,
            'so_field': self.alternative_so.id,
            'su_field':self.alternative_su_ecig.id,
            'ecig_vape_or_start':['V', 'S'],
            }
        self.health_sp = ConsoAlternative.objects.create(
            user=self.usertest,
            date_alter=datetime.date(2020, 5, 17),
            time_alter=datetime.time(13, 15),
            alternative=self.alternative_sp,
            activity_duration=90,
        )
        self.data_id = {'id_health': self.health_sp.id}

    def test_get_request_data(self):
        """test HealthManager.get_request_data method"""
        health = HealthManager(self.usertest, self.data_sp)
        self.assertEqual(health.get_request_data('date_health'), datetime.date(2020, 5, 17))
        self.assertEqual(health.get_request_data('time_health'), datetime.time(13, 15))
        self.assertEqual(health.get_request_data('sp_field'), self.alternative_sp.id)

    def test_get_alternative_with_infos(self):
        health = HealthManager(self.usertest, self.data_sp)
        self.assertEqual(health.get_alternative, self.alternative_sp)
        health = HealthManager(self.usertest, self.data_su)
        self.assertEqual(health.get_alternative, self.alternative_su)

    def test_get_alternative_with_id(self):
        health = HealthManager(self.usertest, self.data_id)
        self.assertEqual(health.get_conso_alternative, self.health_sp)
        self.assertEqual(health.get_alternative, self.alternative_sp)

    def test_get_duration(self):
        health = HealthManager(self.usertest, self.data_sp)
        self.assertEqual(health.get_duration, 90)

    def test_get_ecig_data(self):
        health = HealthManager(self.usertest, self.data_su_ecig)
        health.delete_conso_alternative()
        self.assertEqual(health.get_ecig_data, 'VS')
        self.data_su_ecig['ecig_vape_or_start'] = ['S', 'V']
        self.assertEqual(health.get_ecig_data, 'VS')
        self.data_su_ecig['ecig_vape_or_start'] = ['V']
        self.assertEqual(health.get_ecig_data, 'V')
        self.data_su_ecig['ecig_vape_or_start'] = ['S']
        self.assertEqual(health.get_ecig_data, 'S')
        self.data_su_ecig['ecig_vape_or_start'] = []
        self.assertEqual(health.get_ecig_data, None)
        del self.data_su_ecig['ecig_vape_or_start']
        self.assertEqual(health.get_ecig_data, None)

    def test_get_conso_alternative_with_infos(self):
        health = HealthManager(self.usertest, self.data_sp)
        self.assertEqual(health.get_conso_alternative, self.health_sp)

    def test_create_conso_alternative(self):
        new_health = HealthManager(self.usertest, self.data_su)
        new = new_health.create_conso_alternative()
        self.assertTrue(new)
        self.assertEqual(new_health.get_alternative.id, self.alternative_su.id)

    def test_create_conso_alternative_ecig(self):
        new_health = HealthManager(self.usertest, self.data_su_ecig)
        new = new_health.create_conso_alternative()
        self.assertTrue(new)
        self.assertEqual(new.ecig_choice,  'VS')

    def test_create_conso_cig_datas_id(self):
        """test HealtheManager.create_conso_alternative method with id_alternative in request"""
        new_health = HealthManager(self.usertest, self.data_id)
        self.assertEqual(new_health.create_conso_alternative(), None)

    def test_delete_conso_cig_given_cig(self):
        """test HealtheManager.create_conso_alternative method with data"""
        health = HealthManager(self.usertest, self.data_id)
        health.delete_conso_alternative()
        filter_conso = ConsoAlternative.objects.filter(user=self.usertest, id=self.data_id['id_health'])
        self.assertFalse(filter_conso.exists())

    def test_delete_conso_cig_given_cig(self):
        """test HealtheManager.create_conso_alternative method with data"""
        health = HealthManager(self.usertest, {'id_health': 92})
        health.delete_conso_alternative()
        filter_conso = ConsoAlternative.objects.filter(user=self.usertest, id=92)
        self.assertFalse(filter_conso.exists())
