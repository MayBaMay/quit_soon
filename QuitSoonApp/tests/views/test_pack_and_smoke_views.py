#!/usr/bin/env python

"""tests views related to user paquets or smoking """


from decimal import Decimal
import datetime
import pytz
from freezegun import freeze_time

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from QuitSoonApp.views import (
    UserProfile, paquets, smoke,
)
from QuitSoonApp.models import (
    Paquet, ConsoCig,
)
from QuitSoonApp.forms import PaquetFormCreation, SmokeForm, ChoosePackFormWithEmptyFields
from ..MOCK_DATA import BaseTestCase


class PacksAndSmokeTestCase(BaseTestCase):
    """
    Tests on parameters page packs and smoking page
    """

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.client.login(username=self.usertest.username, password='arandompassword')
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2020-05-13',
            starting_nb_cig=20
        )

    def test_paquets_view_get(self):
        """Test get paquets view"""
        response = self.client.get(reverse('QuitSoonApp:paquets'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/paquets.html')

    def test_paquets_view_post_succes(self):
        """Test client post a form with success"""
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10'}
        response = self.client.post(reverse('QuitSoonApp:paquets'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/paquets.html')
        db_pack = self.filter_pack_camel
        self.assertTrue(db_pack.exists())
        self.assertEqual(db_pack[0].unit, 'U')
        self.assertEqual(db_pack[0].g_per_cig, None)

    def test_paquets_view_post_fails(self):
        """Test client post a form with invalid data"""
        brandtest = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        data = {'type_cig':'ROL',
                'brand':'BRANDTEST',
                'qt_paquet':'50',
                'price':'30'}
        response = self.client.post(reverse('QuitSoonApp:paquets'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/paquets.html')
        db_pack = Paquet.objects.filter(
            user=self.usertest,
            type_cig='ROL',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        self.assertEqual(db_pack.count(), 1)
        self.assertEqual(db_pack[0].id, brandtest.id)

    def test_delete_pack_views(self):
        """Test client post delete_pack view"""
        db_pack = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        response = self.client.post(reverse(
            'QuitSoonApp:delete_pack',
            args=[db_pack.id]))
        self.assertEqual(response.status_code, 302)
        filter = Paquet.objects.filter(
            user=self.usertest,
            type_cig='ROL',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        self.assertFalse(filter.exists())

    def test_delete_pack_views_wrong_arg(self):
        response = self.client.post(reverse(
            'QuitSoonApp:delete_pack',
            args=[3453]))
        self.assertEqual(response.status_code, 404)

    def test_change_g_per_cig_view(self):
        """Test client post hange_g_per_cig view"""
        pack = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='BRANDTEST',
            qt_paquet=40,
            price=100,
            )
        self.assertEqual(pack.g_per_cig, None)
        data = {'type_cig':'ROL',
                'brand':'BRANDTEST',
                'qt_paquet':'40',
                'price':'100',
                'g_per_cig':'1.1'
                }
        response = self.client.post(reverse('QuitSoonApp:change_g_per_cig'),
                                    data=data)
        paquet = Paquet.objects.get(
            id=pack.id,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(paquet.g_per_cig, Decimal('1.1'))
        self.assertEqual(paquet.price_per_cig, Decimal('2.75'))

    def test_smoke_get_no_pack(self):
        """ test get smoke view with no pack saved by user """
        response = self.client.get(reverse('QuitSoonApp:smoke'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['packs'].exists())
        self.assertFalse(response.context['smoke'].exists())

    def test_smoke_get_form(self):
        """ test get smoke view with packs saved by user, get form"""
        db_pack_ind = self.camel
        response = self.client.get(reverse('QuitSoonApp:smoke'))
        self.assertTrue(response.context['packs'].exists())
        self.assertFalse(response.context['smoke'].exists())
        self.assertTrue('smoke_form' in response.context)

    def test_smoke_post_validform_given_true(self):
        """ test post smoke view with given=True """
        db_pack_ind = Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='NEW BRAND',
            qt_paquet=20,
            price=11,
            )
        data = {
            'date_smoke':datetime.date(2020, 5, 26),
            'time_smoke':datetime.time(12, 56),
            'type_cig_field':'IND',
            'indus_pack_field':db_pack_ind.id,
            'given_field':True,
            }
        response = self.client.post(reverse('QuitSoonApp:smoke'),
                                    data=data)
        filter_smoke = ConsoCig.objects.filter(
            user=self.usertest,
        )
        self.assertTrue(filter_smoke.exists())
        self.assertEqual(filter_smoke.count(), 1)

    def test_smoke_post_validform_given_false(self):
        """ test post smoke view with given=false """
        db_pack_ind = self.camel
        db_pack_ind2 = self.philip_morris
        db_pack_rol = self.rol_1637
        data = {
            'date_smoke':datetime.date(2020, 5, 26),
            'time_smoke':datetime.time(12, 56),
            'type_cig_field':'IND',
            'indus_pack_field':db_pack_ind.id,
            'rol_pack_field':db_pack_rol.id,
            'given_field':False,
            }
        response = self.client.post(reverse('QuitSoonApp:smoke'), data=data)
        filter_smoke = ConsoCig.objects.filter(
            user=self.usertest,
        )
        self.assertTrue(filter_smoke.exists())
        self.assertEqual(filter_smoke.count(), 1)

    @freeze_time("2020-05-26 20:21:34")
    def test_smoke_get_lastsmoke(self):
        """ test get smoke view with packs saved by user, get form"""
        db_pack_ind = self.camel
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 26, 12, 5, tzinfo=pytz.utc),
            paquet=db_pack_ind,
            given=False,
        )
        response = self.client.get(reverse('QuitSoonApp:smoke'))
        self.assertEqual(response.context['lastsmoke'], ['8 heures ', '16 minutes '])


    def test_delete_smoke_fail(self):
        """ test get delete_smoke view with unexisting ConsoCig """
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[40]))
        self.assertEqual(response.status_code, 404)

    def test_delete_smoke_given_true(self):
        """ test get delete_smoke smoke.given=True """
        db_smoke_given = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 17, 13, 15, tzinfo=pytz.utc),
            paquet=None,
            given=True,
            )
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[db_smoke_given.id]))
        self.assertEqual(response.status_code, 302)
        filter_conso = ConsoCig.objects.filter(user=self.usertest, id=db_smoke_given.id)
        self.assertFalse(filter_conso.exists())

    def test_delete_smoke_given_false(self):
        """ test get delete_smoke smoke.given=False """
        db_pack = self.camel
        db_smoke = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 17, 13, 15, tzinfo=pytz.utc),
            paquet=db_pack,
            given=False,
            )
        id = db_smoke.id
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[db_smoke.id]))
        self.assertEqual(response.status_code, 302)
        filter_conso = ConsoCig.objects.filter(user=self.usertest, id=id)
        self.assertFalse(filter_conso.exists())


class SmokeListTestCase(BaseTestCase):

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.client.login(username=self.usertest.username, password='arandompassword')
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2020-05-13',
            starting_nb_cig=20
        )

        self.db_pack_undisplayed = self.lucky
        self.db_pack_ind = self.camel
        self.db_pack_ind2 = self.philip_morris
        self.db_pack_rol = self.rol_1637
        self.db_pack_nb = self.beedies

        self.bd_consocig0 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 9, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_rol,
            given=False,
        )
        self.bd_consocig1 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 9, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )
        self.bd_consocig2 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 11, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )
        self.bd_consocig3 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 22, 5, tzinfo=pytz.utc),
            paquet=None,
            given=True,
        )
        self.bd_consocig4 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 22, 35, tzinfo=pytz.utc),
            paquet=self.db_pack_ind2,
            given=False,
        )

    def test_smoke_list_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('QuitSoonApp:smoke_list'))
        self.assertEqual(response.status_code, 302)

    def test_smoke_list_no_pack_saved(self):
        Paquet.objects.filter(user=self.usertest).delete()
        response = self.client.get(reverse('QuitSoonApp:smoke_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['packs'].count(), 0)
        self.assertTrue('smoke' not in response.context.keys())
        self.assertTrue('smoke_list_form' not in response.context.keys())

    def test_smoke_list_no_smoke_saved(self):
        ConsoCig.objects.filter(user=self.usertest).delete()
        response = self.client.get(reverse('QuitSoonApp:smoke_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['packs'], Paquet.objects.filter(user=self.usertest, display=True))
        self.assertTrue('smoke' not in response.context.keys())
        self.assertTrue('smoke_list_form' not in response.context.keys())

    def test_smoke_list_empty_fields(self):
        data = {'type_cig_field':'empty',
                'ind_pack_field':'empty',
                'rol_pack_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:smoke_list'),
                                    data=data)
        self.assertTrue(response.context['packs'], Paquet.objects.filter(user=self.usertest, display=True))
        self.assertTrue(response.context['smoke'][0], self.bd_consocig4)
        self.assertTrue(response.context['smoke'][1], self.bd_consocig3)
        self.assertTrue(response.context['smoke'][2], self.bd_consocig2)
        self.assertTrue(response.context['smoke'][3], self.bd_consocig1)
        self.assertTrue(response.context['smoke'][4], self.bd_consocig0)
        self.assertEqual(len(response.context['smoke']), 5)
        self.assertTrue('smoke_list_form' in response.context.keys())

    def test_smoke_list_given(self):
        data = {'type_cig_field':'given'}
        response = self.client.post(reverse('QuitSoonApp:smoke_list'),
                                    data=data)
        self.assertTrue(response.context['smoke'][0], self.bd_consocig3)
        self.assertTrue(self.bd_consocig2 not in response.context['smoke'])
        self.assertTrue('smoke_list_form' in response.context.keys())

    def test_only_type_cig_field(self):
        data = {'type_cig_field':'IND',
                'ind_pack_field':'empty',
                'rol_pack_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:smoke_list'),
                                    data=data)
        self.assertTrue(response.context['smoke'][0], self.bd_consocig4)
        self.assertTrue(response.context['smoke'][1], self.bd_consocig2)
        self.assertTrue(response.context['smoke'][2], self.bd_consocig1)
        self.assertEqual(len(response.context['smoke']), 3)
        self.assertTrue('smoke_list_form' in response.context.keys())

    def test_only_ind_pack_field(self):
        data = {'type_cig_field':'IND',
                'ind_pack_field': self.db_pack_ind2.id,
                'rol_pack_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:smoke_list'),
                                    data=data)
        self.assertTrue(response.context['smoke'][0], self.bd_consocig4)
        self.assertEqual(len(response.context['smoke']), 1)
        self.assertTrue('smoke_list_form' in response.context.keys())

    def test_only_rol_pack_field(self):
        data = {'type_cig_field':'ROL',
                'ind_pack_field': 'empty',
                'rol_pack_field':self.db_pack_rol.id}
        response = self.client.post(reverse('QuitSoonApp:smoke_list'),
                                    data=data)
        self.assertTrue(response.context['smoke'][0], self.bd_consocig0)
        self.assertEqual(len(response.context['smoke']), 1)
        self.assertTrue('smoke_list_form' in response.context.keys())
