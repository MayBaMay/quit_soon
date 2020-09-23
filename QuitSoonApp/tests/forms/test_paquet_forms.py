#!/usr/bin/env python

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from QuitSoonApp.forms import (
    PaquetFormCreation,
    PaquetFormCustomGInCig,
    )
from QuitSoonApp.models import Paquet

class test_PaquetFormCreation(TestCase):
    """test PaquetFormCreation"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")

    def test_PaquetFormCreation_is_valid(self):
        """test valid PaquetFormCreation"""
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10'}
        form = PaquetFormCreation(self.user, data)
        self.assertTrue(form.is_valid())

    def test_PaquetFormCreation_is_not_valid(self):
        """test invalid PaquetFormCreation, data already in DB"""
        Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10'}
        form = PaquetFormCreation(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

class test_PaquetFormCustomGInCig(TestCase):
    """test PaquetFormCustomGInCig"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")


    def test_PaquetFormCustomGInCig_is_valid(self):
        """test valid PaquetFormCustomGInCig"""
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10',
                'g_per_cig':'0.9'}
        form = PaquetFormCustomGInCig(self.user, data)
        self.assertTrue(form.is_valid())
