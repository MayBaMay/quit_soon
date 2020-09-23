#!/usr/bin/env python

import datetime
import pytz
from freezegun import freeze_time

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from QuitSoonApp.forms import (
    PaquetFormCreation,
    PaquetFormCustomGInCig,
    ChoosePackFormWithEmptyFields
    )
from QuitSoonApp.models import Paquet, ConsoCig
from ..MOCK_DATA import BaseTestCase, BaseAllPacksTestCase


class PaquetFormCreationTestCase(BaseTestCase):
    """test PaquetFormCreation"""

    def setUp(self):
        """setup tests"""
        super().setUp()

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
        self.camel
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10'}
        form = PaquetFormCreation(self.usertest, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

    def test_clean_brand(self):
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
        self.db_pack_ind = self.camel
        data = {
            'type_cig':'IND',
            'brand':'camel',
            'qt_paquet':20,
            'price':10,
            }
        form = PaquetFormCreation(self.usertest, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)


class test_PaquetFormCustomGInCig(BaseTestCase):
    """test PaquetFormCustomGInCig"""

    def setUp(self):
        """setup tests"""
        super().setUp()

    def test_PaquetFormCustomGInCig_is_valid(self):
        """test valid PaquetFormCustomGInCig"""
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10',
                'g_per_cig':'0.9'}
        form = PaquetFormCustomGInCig(self.usertest, data)
        self.assertTrue(form.is_valid())


class ChoosePackFormWithEmptyFieldsTestCase(BaseAllPacksTestCase):

    def test_config_fields(self):
        bd_consocig1 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 11, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )
        bd_consocig2 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 11, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )
        bd_consocig3 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 22, 5, tzinfo=pytz.utc),
            paquet=None,
            given=True,
        )
        form = ChoosePackFormWithEmptyFields(self.usertest)
        self.assertEqual(form.initial['type_cig_field'], ('empty', '------------------'))
        self.assertEqual(form.fields['type_cig_field'].choices[1][0],'IND')
        self.assertEqual(form.fields['type_cig_field'].choices[2],('given', 'Clopes taxées'))
        self.assertEqual(form.initial['ind_pack_field'], ('empty', '------------------'))
        self.assertEqual(form.fields['ind_pack_field'].choices[1],(self.db_pack_ind.id, 'CAMEL /20U'))
        self.assertEqual(form.initial['rol_pack_field'], ('empty', '------------------'))


    def test_valid_empty_data(self):
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
