#!/usr/bin/env python

"""Module testing save_smoke module"""

import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import Paquet, ConsoCig
from QuitSoonApp.modules import SmokeManager


class SmokeManagerTestCase(TestCase):
    """class testing SmokeManager """

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.db_pack_ind = Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        self.db_pack_rol = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='1637',
            qt_paquet=30,
            price=12,
            )
        self.db_smoke_ind = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 17, 10, 15, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            )
        self.new_datas_ind = {
            'date_smoke': datetime.date(2020, 5, 17),
            'time_smoke': datetime.time(13, 15),
            'type_cig_field':'IND',
            'ind_pack_field':self.db_pack_ind.id,
            'rol_pack_field': self.db_pack_rol.id,
            'given_field':False,
            }
        self.new_datas_rol = data ={
            'date_smoke': datetime.date(2020, 5, 17),
            'time_smoke': datetime.time(13, 15),
            'type_cig_field':'ROL',
            'ind_pack_field':self.db_pack_ind.id,
            'rol_pack_field': self.db_pack_rol.id,
            'given_field':False,
            }
        self.old_smoke_ind_data = {'id_smoke': self.db_smoke_ind.id}

    def test_get_request_data(self):
        """test SmokeManager.get_request_data method"""
        smoke = SmokeManager(self.usertest, self.new_datas_ind)
        self.assertEqual(smoke.get_request_data('date_smoke'), datetime.date(2020, 5, 17))
        self.assertEqual(smoke.get_request_data('time_smoke'), datetime.time(13, 15))
        self.assertEqual(smoke.get_request_data('ind_pack_field'), self.db_pack_ind.id)

    def test_invalid_datetime(self):
        """test if date or time invalid in args"""
        data = {
            'date_smoke': 'invalid',
            'time_smoke': datetime.time(14, 15),
            'type_cig_field':'ROL',
            'ind_pack_field':self.db_pack_ind.id,
            'rol_pack_field': self.db_pack_rol.id,
            'given_field':False,
            }
        smoke = SmokeManager(self.usertest, data)
        self.assertEqual(smoke.datetime_cig, None)

    def test_get_pack_ind(self):
        """test SmokeManager.get_pack method with new smoke data and given_field=False & type_cig_field='IND'"""
        smoke = SmokeManager(self.usertest, self.new_datas_ind)
        self.assertEqual(smoke.get_pack, self.db_pack_ind)
        self.assertEqual(smoke.get_pack, self.db_pack_ind)

    def test_get_pack_rol(self):
        """test SmokeManager.get_pack method with new smoke data : given_field=False & type_cig_field='ROL'"""
        smoke = SmokeManager(self.usertest, self.new_datas_rol)
        self.assertEqual(smoke.get_pack, self.db_pack_rol)
        self.assertEqual(smoke.get_pack, self.db_pack_rol)

    def test_get_pack__given_cig(self):
        """test SmokeManager.get_pack method with new smoke data and given_field=True"""
        self.new_datas_ind['given_field'] = True
        smoke = SmokeManager(self.usertest, self.new_datas_ind)
        self.assertEqual(smoke.get_pack, None)
        self.assertEqual(smoke.get_pack, None)

    def test_get_pack_smoke_id(self):
        """test SmokeManager.get_pack method with id_smoke in data (for delete_smoke view)"""
        smoke = SmokeManager(self.usertest, self.old_smoke_ind_data)
        self.assertEqual(smoke.get_pack, self.db_pack_ind)
        self.assertEqual(smoke.get_pack, self.db_pack_ind)

    def test_get_pack_smoke_fail(self):
        """ test method get get_pack fail, exception raised cause wrong id"""
        smoke = SmokeManager(self.usertest, 10394)
        self.assertEqual(smoke.get_pack, None)

    def test_create_conso_cig(self):
        """test SmokeManager.create_conso_cig method with new conso data"""
        smoke = SmokeManager(self.usertest, self.new_datas_ind)
        smoke.create_conso_cig()
        new_smoke = ConsoCig.objects.filter(user=self.usertest,
                             datetime_cig=datetime.datetime(2020, 5, 17, 13, 15, tzinfo=pytz.utc),
                             paquet=self.db_pack_ind,
                             given=False)
        self.assertTrue(new_smoke.exists())
        self.assertEqual(smoke.get_pack.id, self.db_pack_ind.id)

    def test_create_conso_cig_datas_id_smoke(self):
        """test SmokeManager.create_conso_cig method with id_smoke in request"""
        smoke = SmokeManager(self.usertest, self.old_smoke_ind_data)
        self.assertEqual(smoke.create_conso_cig(), None)

    def test_create_conso_cig_given(self):
        """ test SmokeManager.create_conso_cig method with given=True """
        new_datas_given_cig = {
            'date_smoke': datetime.date(2020, 7, 15),
            'time_smoke': datetime.time(20, 15),
            'ind_pack_field':self.db_pack_ind.id,
            'rol_pack_field': self.db_pack_rol.id,
            'given_field':True,
            }
        smoke = SmokeManager(self.usertest, new_datas_given_cig)
        smoke.create_conso_cig()
        self.assertEqual(smoke.get_pack, None)
        new_given_smoke = ConsoCig.objects.filter(user=self.usertest,
                             datetime_cig=datetime.datetime(2020, 7, 15, 20, 15, tzinfo=pytz.utc),
                             paquet=None,
                             given=True)
        self.assertTrue(new_given_smoke.exists())


    def test_get_conso_cig_id_smoke(self):
        """test SmokeManager.conso_cig method with id_smoke in request"""
        smoke = SmokeManager(self.usertest, self.old_smoke_ind_data)
        self.assertEqual(smoke.get_conso_cig, self.db_smoke_ind)

    def test_get_conso_cig_new_conso(self):
        """test SmokeManager.conso_cig method after creation object with new conso data"""
        smoke = SmokeManager(self.usertest, self.new_datas_ind)
        smoke.create_conso_cig()
        self.assertEqual(smoke.get_conso_cig, ConsoCig.objects.get(
            user=self.usertest,
            datetime_cig=smoke.datetime_cig,
            paquet=smoke.get_pack,
            given=smoke.given,
            ))

    def test_get_conso_cig_not_created(self):
        """test SmokeManager.conso_cig method without creating object with new conso data"""
        smoke = SmokeManager(self.usertest, self.new_datas_ind)
        self.assertEqual(smoke.get_conso_cig, None)

    def test_delete_conso_cig(self):
        """test SmokeManager.delete_conso method"""
        smoke = SmokeManager(self.usertest, self.old_smoke_ind_data)
        smoke.delete_conso_cig()
        filter_conso = ConsoCig.objects.filter(user=self.usertest, paquet=self.db_pack_ind.id)
        self.assertFalse(filter_conso.exists())

    def test_delete_conso_cig(self):
        """test SmokeManager.delete_conso method"""
        smoke = SmokeManager(self.usertest, {'id_smoke': 17364})
        self.assertRaises(AttributeError, smoke.delete_conso_cig())

    def test_delete_conso_cig_given_cig(self):
        """test SmokeManager.delete_conso method with cig == given cig"""
        db_smoke_given = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 17, 13, 15, tzinfo=pytz.utc),
            paquet=None,
            )
        data = {'id_smoke': db_smoke_given.id}
        smoke = SmokeManager(self.usertest, data)
        smoke.delete_conso_cig()
        filter_conso = ConsoCig.objects.filter(user=self.usertest, id=db_smoke_given.id)
        self.assertFalse(filter_conso.exists())
