#!/usr/bin/env python

"""Module testing save_smoke module"""

import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import Paquet, ConsoCig
from QuitSoonApp.modules import SaveSmoke


class SaveSmokeTestCase(TestCase):
    """class testing SaveSmoke """

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
            date_cig=datetime.date(2020, 6, 17),
            time_cig=datetime.time(10, 15),
            paquet=self.db_pack_ind,
            )
        self.new_datas_ind = {
            'date_smoke': datetime.date(2020, 5, 17),
            'time_smoke': datetime.time(13, 15),
            'type_cig_field':'IND',
            'indus_pack_field':self.db_pack_ind.id,
            'rol_pack_field': self.db_pack_rol.id,
            'given_field':False,
            }
        self.new_datas_rol = datas ={
            'date_smoke': datetime.date(2020, 5, 17),
            'time_smoke': datetime.time(13, 15),
            'type_cig_field':'ROL',
            'indus_pack_field':self.db_pack_ind.id,
            'rol_pack_field': self.db_pack_rol.id,
            'given_field':False,
            }
        self.old_smoke_ind_data = {'id_smoke': self.db_smoke_ind.id}

    def test_get_request_data(self):
        """test SaveSmoke.get_request_data method"""
        smoke = SaveSmoke(self.usertest, self.new_datas_ind)
        self.assertEqual(smoke.get_request_data('date_smoke'), datetime.date(2020, 5, 17))
        self.assertEqual(smoke.get_request_data('time_smoke'), datetime.time(13, 15))
        self.assertEqual(smoke.get_request_data('indus_pack_field'), self.db_pack_ind.id)

    def tes_get_pack_ind(self):
        """test SaveSmoke.get_pack method with new smoke datas and given_field=False & type_cig_field='IND'"""
        smoke = SaveSmoke(self.usertest, self.new_datas_ind)
        self.assertEqual(smoke.get_pack, self.db_pack_ind)
        self.assertEqual(smoke.paquet, self.db_pack_ind)

    def test_get_pack_rol(self):
        """test SaveSmoke.get_pack method with new smoke datas : given_field=False & type_cig_field='ROL'"""
        smoke = SaveSmoke(self.usertest, self.new_datas_rol)
        self.assertEqual(smoke.get_pack, self.db_pack_rol)
        self.assertEqual(smoke.paquet, self.db_pack_rol)

    def test_get_pack__given_cig(self):
        """test SaveSmoke.get_pack method with new smoke datas and given_field=True"""
        self.new_datas_ind['given_field'] = True
        smoke = SaveSmoke(self.usertest, self.new_datas_ind)
        self.assertEqual(smoke.get_pack, None)
        self.assertEqual(smoke.paquet, None)

    def test_get_pack_smoke_id(self):
        """test SaveSmoke.get_pack method with id_smoke in datas (for delete_smoke view)"""
        smoke = SaveSmoke(self.usertest, self.old_smoke_ind_data)
        self.assertEqual(smoke.get_pack, self.db_pack_ind)
        self.assertEqual(smoke.paquet, self.db_pack_ind)

    def test_create_conso_cig(self):
        """test SaveSmoke.create_conso_cig method with new conso datas"""
        smoke = SaveSmoke(self.usertest, self.new_datas_ind)
        smoke.create_conso_cig()
        new_smoke = ConsoCig.objects.filter(user=self.usertest,
                             date_cig=datetime.date(2020, 5, 17),
                             time_cig=datetime.time(13, 15),
                             paquet=self.db_pack_ind,
                             given=False)
        self.assertTrue(new_smoke.exists())
        self.assertEqual(smoke.paquet.id, self.db_pack_ind.id)

    def test_create_conso_cig_datas_id_smoke(self):
        """test SaveSmoke.create_conso_cig method with id_smoke in request"""
        smoke = SaveSmoke(self.usertest, self.old_smoke_ind_data)
        self.assertEqual(smoke.create_conso_cig(), None)

    def test_create_conso_cig_given(self):
        """ test SaveSmoke.create_conso_cig method with given=True """
        new_datas_given_cig = {
            'date_smoke': datetime.date(2020, 7, 15),
            'time_smoke': datetime.time(20, 15),
            'indus_pack_field':self.db_pack_ind.id,
            'rol_pack_field': self.db_pack_rol.id,
            'given_field':True,
            }
        smoke = SaveSmoke(self.usertest, new_datas_given_cig)
        smoke.create_conso_cig()
        self.assertEqual(smoke.paquet, None)
        new_given_smoke = ConsoCig.objects.filter(user=self.usertest,
                             date_cig=datetime.date(2020, 7, 15),
                             time_cig=datetime.time(20, 15),
                             paquet=None,
                             given=True)
        self.assertTrue(new_given_smoke.exists())


    def test_get_conso_cig_id_smoke(self):
        """test SaveSmoke.conso_cig method with id_smoke in request"""
        smoke = SaveSmoke(self.usertest, self.old_smoke_ind_data)
        self.assertEqual(smoke.get_conso_cig, self.db_smoke_ind)

    def test_get_conso_cig_new_conso(self):
        """test SaveSmoke.conso_cig method after creation object with new conso datas"""
        smoke = SaveSmoke(self.usertest, self.new_datas_ind)
        smoke.create_conso_cig()
        self.assertEqual(smoke.get_conso_cig, ConsoCig.objects.get(
            user=self.usertest,
            date_cig=smoke.date_cig,
            time_cig=smoke.time_cig,
            paquet=smoke.paquet,
            given=smoke.given,
            ))

    def test_get_conso_cig_not_created(self):
        """test SaveSmoke.conso_cig method without creating object with new conso datas"""
        smoke = SaveSmoke(self.usertest, self.new_datas_ind)
        self.assertEqual(smoke.get_conso_cig, None)

    def test_delete_conso_cig(self):
        """test SaveSmoke.delete_conso method"""
        smoke = SaveSmoke(self.usertest, self.old_smoke_ind_data)
        smoke.delete_conso_cig()
        filter_conso = ConsoCig.objects.filter(user=self.usertest, paquet=self.db_pack_ind.id)
        self.assertFalse(filter_conso.exists())

    def test_delete_conso_cig_given_cig(self):
        """test SaveSmoke.delete_conso method with cig == given cig"""
        db_smoke_given = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 5, 17),
            time_cig=datetime.time(13, 15),
            paquet=None,
            )
        data = {'id_smoke': db_smoke_given.id}
        smoke = SaveSmoke(self.usertest, data)
        smoke.delete_conso_cig()
        filter_conso = ConsoCig.objects.filter(user=self.usertest, id=db_smoke_given.id)
        self.assertFalse(filter_conso.exists())
