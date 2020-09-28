#!/usr/bin/env python
# pylint: disable=C0103 #Method name "test_smokeForm_is_valid" doesn't conform to snake_case naming style (invalid-name)
# pylint: disable=C0103 #Class name "test_PaquetFormCustomGInCig" doesn't conform to PascalCase naming style (invalid-name)
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code


"""Test forms related to Paquet model"""

import datetime
import pytz

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from QuitSoonApp.forms import (
    PaquetFormCreation,
    PaquetFormCustomGInCig,
    ChoosePackFormWithEmptyFields
    )
from QuitSoonApp.models import Paquet, ConsoCig


class PaquetFormCreationTestCase(TestCase):
    """test PaquetFormCreation"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_PaquetFormCreation_is_valid(self):
        """test valid PaquetFormCreation"""
        data = {
            'type_cig':'IND',
            'brand':'camel',
            'qt_paquet':20,
            'price':10,
            }
        form = PaquetFormCreation(self.usertest, data)
        self.assertTrue(form.is_valid())

    def test_PaquetFormCreation_is_not_valid(self):
        """test invalid PaquetFormCreation, data already in DB"""
        Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
        )
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10'}
        form = PaquetFormCreation(self.usertest, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

    def test_clean_brand(self):
        """test PaquetFormCreation brand field cleaning method"""
        data = {
            'type_cig':'IND',
            'brand':'camel',
            'qt_paquet':20,
            'price':10,
            }
        form = PaquetFormCreation(self.usertest, data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('brand'), 'CAMEL')

    def test_clean(self):
        """test PaquetFormCreation general cleaning method"""
        Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        data = {
            'type_cig':'IND',
            'brand':'camel',
            'qt_paquet':20,
            'price':10,
            }
        form = PaquetFormCreation(self.usertest, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)


class test_PaquetFormCustomGInCig(TestCase):
    """test PaquetFormCustomGInCig"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_PaquetFormCustomGInCig_is_valid(self):
        """test valid PaquetFormCustomGInCig"""
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10',
                'g_per_cig':'0.9'}
        form = PaquetFormCustomGInCig(self.usertest, data)
        self.assertTrue(form.is_valid())


class ChoosePackFormWithEmptyFieldsTestCase(TestCase):
    """test ChoosePackFormWithEmptyFields"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.db_pack_undisplayed = Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='LUCKY',
            qt_paquet=20,
            price=10,
            display=False
            )
        self.db_pack_ind = Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        self.db_pack_ind2 = Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='PHILIP MORRIS',
            qt_paquet=20,
            price=10.2,
            )
        self.db_pack_rol = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='1637',
            qt_paquet=30,
            price=12,
            )
        self.db_pack_nb = Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='BEEDIES',
            qt_paquet=30,
            price=5,
            )

    def test_config_fields(self):
        """test ChoosePackFormWithEmptyFields config_fields"""
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 11, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 11, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 22, 5, tzinfo=pytz.utc),
            paquet=None,
            given=True,
        )
        form = ChoosePackFormWithEmptyFields(self.usertest)
        self.assertEqual(
            form.initial['type_cig_field'], ('empty', '------------------')
            )
        self.assertEqual(
            form.fields['type_cig_field'].choices[1][0],'IND'
            )
        self.assertEqual(
            form.fields['type_cig_field'].choices[2],('given', 'Clopes taxées')
            )
        self.assertEqual(
            form.initial['ind_pack_field'], ('empty', '------------------')
            )
        self.assertEqual(
            form.fields['ind_pack_field'].choices[1],(self.db_pack_ind.id, 'CAMEL /20U')
            )
        self.assertEqual(
            form.initial['rol_pack_field'], ('empty', '------------------')
            )


    def test_valid_empty_data(self):
        """
        test ChoosePackFormWithEmptyFields is still valid with empty data
        """
        data = {'type_cig_field':'empty'}
        form = ChoosePackFormWithEmptyFields(self.usertest, data)
        self.assertTrue(form.is_valid())

        data = {
            'type_cig_field':'empty',
            'ind_pack_field':'empty',
            'rol_pack_field':'empty',
            }
        form = ChoosePackFormWithEmptyFields(self.usertest, data)
        self.assertTrue(form.is_valid())
