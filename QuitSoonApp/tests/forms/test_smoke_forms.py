#!/usr/bin/env python

import datetime

from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from QuitSoonApp.forms import SmokeForm
from QuitSoonApp.models import Paquet, ConsoCig

class test_SmokeForm(TestCase):
    """test PaquetFormCreation"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")
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
        self.db_pack_nb = Paquet.objects.create(
            user=self.usertest,
            type_cig='NB',
            brand='beedies',
            qt_paquet=30,
            price=5,
            )
        self.valid_datas = {
            'date_smoke':datetime.date(2020, 5, 26),
            'time_smoke':datetime.time(12, 56),
            'type_cig_field':'IND',
            'indus_pack_field':self.db_pack_ind.id,
            'rol_pack_field':self.db_pack_rol.id,
            'cigares_pack_field':None,
            'pipe_pack_field':None,
            'nb_pack_field':self.db_pack_nb.id,
            'gr_pack_field':None,
            'given_field':False,
            }


    def test_SmokeForm_is_valid(self):
        """test valid SmokeForm"""
        form = SmokeForm(self.usertest, self.valid_datas)
        self.assertTrue(form.is_valid())

    def test_SmokeForm_is_not_valid(self):
        """test invalid SmokeForm, datas already in DB"""
