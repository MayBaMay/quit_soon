#!/usr/bin/env python

from decimal import Decimal
import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from QuitSoonApp.views import (
    paquets, smoke,
)
from QuitSoonApp.models import (
    Paquet, ConsoCig,
)


class PacksAndSmokeTestCase(TestCase):
    """
    Tests on parameters page packs and smoking page
    """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'TestUser', 'test@test.com', 'testpassword')
        self.client.login(username=self.user.username, password='testpassword')

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
        db_pack = Paquet.objects.filter(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        self.assertTrue(db_pack.exists())
        self.assertEqual(db_pack[0].unit, 'U')
        self.assertEqual(db_pack[0].g_per_cig, None)

    def test_paquets_view_post_fails(self):
        """Test client post a form with invalid datas"""
        brandtest = Paquet.objects.create(
            user=self.user,
            type_cig='GR',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        datas = {'type_cig':'GR',
                'brand':'BRANDTEST',
                'qt_paquet':'50',
                'price':'30'}
        response = self.client.post(reverse('QuitSoonApp:paquets'),
                                    data=datas)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/paquets.html')
        db_pack = Paquet.objects.filter(
            user=self.user,
            type_cig='GR',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        self.assertEqual(db_pack.count(), 1)
        self.assertEqual(db_pack[0].id, brandtest.id)

    def test_delete_pack_views(self):
        """Test client post delete_pack view"""
        db_pack = Paquet.objects.create(
            user=self.user,
            type_cig='GR',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        response = self.client.post(reverse(
            'QuitSoonApp:delete_pack',
            args=[db_pack.id]))
        self.assertEqual(response.status_code, 302)
        filter = Paquet.objects.filter(
            user=self.user,
            type_cig='GR',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        self.assertFalse(filter.exists())

    def test_change_g_per_cig_view(self):
        """Test client post hange_g_per_cig view"""
        pack = Paquet.objects.create(
            user=self.user,
            type_cig='PIPE',
            brand='BRANDTEST',
            qt_paquet=40,
            price=100,
            )
        self.assertEqual(pack.g_per_cig, None)
        data = {'type_cig':'PIPE',
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
        db_pack_ind = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        response = self.client.get(reverse('QuitSoonApp:smoke'))
        self.assertTrue(response.context['packs'].exists())
        self.assertFalse(response.context['smoke'].exists())
        self.assertTrue('form' in response.context)

    def test_smoke_post_validform_given_true(self):
        """ test post smoke view with given=True """
        db_pack_ind = Paquet.objects.create(
            user=self.user,
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
            user=self.user,
        )
        self.assertTrue(filter_smoke.exists())
        self.assertEqual(filter_smoke.count(), 1)

    def test_smoke_post_validform_given_false(self):
        """ test post smoke view with given=false """
        db_pack_ind = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        db_pack_ind2 = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='PHILIP MORRIS',
            qt_paquet=20,
            price=10.2,
            )
        db_pack_rol = Paquet.objects.create(
            user=self.user,
            type_cig='ROL',
            brand='1637',
            qt_paquet=30,
            price=12,
            )
        db_pack_nb = Paquet.objects.create(
            user=self.user,
            type_cig='NB',
            brand='beedies',
            qt_paquet=30,
            price=5,
            )
        data = {
            'date_smoke':datetime.date(2020, 5, 26),
            'time_smoke':datetime.time(12, 56),
            'type_cig_field':'IND',
            'indus_pack_field':db_pack_ind.id,
            'rol_pack_field':db_pack_rol.id,
            'nb_pack_field':db_pack_nb.id,
            'given_field':False,
            }
        response = self.client.post(reverse('QuitSoonApp:smoke'), data=data)
        filter_smoke = ConsoCig.objects.filter(
            user=self.user,
        )
        self.assertTrue(filter_smoke.exists())
        self.assertEqual(filter_smoke.count(), 1)

    def test_delete_smoke_fail(self):
        """ test get delete_smoke view with unexisting ConsoCig """
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[40]))
        self.assertEqual(response.status_code, 404)

    def test_delete_smoke_given_true(self):
        """ test get delete_smoke smoke.given=True """
        db_smoke_given = ConsoCig.objects.create(
            user=self.user,
            date_cig=datetime.date(2020, 5, 17),
            time_cig=datetime.time(13, 15),
            paquet=None,
            given=True,
            )
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[db_smoke_given.id]))
        self.assertEqual(response.status_code, 302)
        filter_conso = ConsoCig.objects.filter(user=self.user, id=db_smoke_given.id)
        self.assertFalse(filter_conso.exists())

    def test_delete_smoke_given_false(self):
        """ test get delete_smoke smoke.given=False """
        db_pack = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        db_smoke_given = ConsoCig.objects.create(
            user=self.user,
            date_cig=datetime.date(2020, 5, 17),
            time_cig=datetime.time(13, 15),
            paquet=db_pack,
            given=False,
            )
        id = db_smoke_given.id
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[db_smoke_given.id]))
        self.assertEqual(response.status_code, 302)
        filter_conso = ConsoCig.objects.filter(user=self.user, id=id)
        self.assertFalse(filter_conso.exists())
