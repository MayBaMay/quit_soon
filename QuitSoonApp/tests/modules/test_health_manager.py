#!/usr/bin/env python

"""Module testing health user action manager module"""

import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import Alternative, ConsoAlternative
from QuitSoonApp.modules import HealthManager
from ..MOCK_DATA import BaseTestCase


class HealthManagerTestCase(BaseTestCase):
    """class testing HealthManager """

    def setUp(self):
        """setup tests"""
        super().setUp()
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
        self.health_sp = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 17, 13, 15, tzinfo=pytz.utc),
            alternative=self.alternative_sp,
            activity_duration=90,
        )
        self.data_id = {'id_health': self.health_sp.id}

    def test_invalid_datetime(self):
        """test if date or time invalid in args"""
        data = {
            'date_health': 'invalid',
            'time_health': datetime.time(14, 15),
            'type_alternative_field':'Su',
            'sp_field': self.alternative_sp.id,
            'so_field': self.alternative_so.id,
            'su_field':self.alternative_su.id,
            }
        health = HealthManager(self.usertest, data)
        self.assertEqual(health.datetime_alter, None)

    def test_get_request_data(self):
        """test HealthManager.get_request_data method"""
        health = HealthManager(self.usertest, self.data_sp)
        self.assertEqual(health.get_request_data('date_health'), datetime.date(2020, 5, 17))
        self.assertEqual(health.get_request_data('time_health'), datetime.time(13, 15))
        self.assertEqual(health.get_request_data('sp_field'), self.alternative_sp.id)

    def test_get_alternative_with_infos(self):
        """test get alternative with valid infos"""
        health = HealthManager(self.usertest, self.data_sp)
        self.assertEqual(health.get_alternative, self.alternative_sp)
        health = HealthManager(self.usertest, self.data_su)
        self.assertEqual(health.get_alternative, self.alternative_su)

    def test_get_alternative_with_id(self):
        """test get alternative with valid id"""
        health = HealthManager(self.usertest, self.data_id)
        self.assertEqual(health.get_conso_alternative, self.health_sp)
        self.assertEqual(health.get_alternative, self.alternative_sp)

    def test_get_alternative_fail(self):
        """ test method get alternativ fail, exception raised"""
        health = HealthManager(self.usertest, 10394)
        self.assertEqual(health.get_alternative, None)

    def test_get_duration(self):
        """test get activity duration method"""
        health = HealthManager(self.usertest, self.data_sp)
        self.assertEqual(health.get_duration, 90)

    def test_get_conso_alternative_with_infos(self):
        """test get conso alternative with valid infos"""
        health = HealthManager(self.usertest, self.data_sp)
        self.assertEqual(health.get_conso_alternative, self.health_sp)

    def test_create_conso_alternative(self):
        """test create conso alternative with valid data"""
        new_health = HealthManager(self.usertest, self.data_su)
        new = new_health.create_conso_alternative()
        self.assertTrue(new)
        self.assertEqual(new_health.get_alternative.id, self.alternative_su.id)

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
