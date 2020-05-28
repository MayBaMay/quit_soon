#!/usr/bin/env python

import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.forms import SmokeForm
from QuitSoonApp.models import Paquet, ConsoCig

class test_SmokeForm(TestCase):
    """test PaquetFormCreation"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")
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
            'nb_pack_field':self.db_pack_nb.id,
            'given_field':False,
            }

    def test_SmokeForm_is_valid(self):
        """test valid SmokeForm"""

        form = SmokeForm(self.usertest, self.valid_datas)
        self.assertTrue(form.is_valid())

    def test_SmokeForm_is_not_valid(self):
        """test invalid SmokeForm, datas missing"""
        form = SmokeForm(self.usertest, {})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'date_smoke': ['Ce champ est obligatoire.'],
            'time_smoke': ['Ce champ est obligatoire.'],
            'type_cig_field': ['Ce champ est obligatoire.'],
            })

    def test_last_smoke_first_smoke(self):
        """ test last_smoke method first user ConsoCig"""
        form = SmokeForm(self.usertest, self.valid_datas)
        self.assertEqual(form.last_smoke, self.db_pack_nb)

    def test_smoke_last_none_first_smoke(self):
        """ test last_smoke method with last smoke given=False smoke """
        db_smoke = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 6, 17),
            time_cig=datetime.time(13, 15),
            paquet=self.db_pack_ind2,
            )
        form = SmokeForm(self.usertest, self.valid_datas)
        self.assertEqual(form.last_smoke, self.db_pack_ind2)

    def test_smoke_last_none(self):
        """ test last_smoke method with last one given=True, before exists given=False """
        db_smoke_0 = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 6, 16),
            time_cig=datetime.time(10, 15),
            paquet=self.db_pack_ind2,
            )
        db_smoke_1 = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 6, 17),
            time_cig=datetime.time(10, 15),
            paquet=self.db_pack_nb,
            )
        db_smoke_2 = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 6, 17),
            time_cig=datetime.time(13, 15),
            paquet=None,
            )
        db_smoke_3 = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 6, 17),
            time_cig=datetime.time(13, 15),
            paquet=None,
            )
        form = SmokeForm(self.usertest, self.valid_datas)
        self.assertEqual(form.last_smoke, self.db_pack_nb)

    def test_config_field(self):
        """ test config_field method """
        db_smoke_1 = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 6, 17),
            time_cig=datetime.time(10, 15),
            paquet=self.db_pack_ind2,
            )
        db_smoke_2 = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 6, 17),
            time_cig=datetime.time(13, 15),
            given=True,
            )
        db_smoke_3 = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 6, 17),
            time_cig=datetime.time(13, 15),
            given=True,
            )
        form = SmokeForm(self.usertest, self.valid_datas)
        pack1 = self.db_pack_ind
        pack2 = self.db_pack_ind2
        self.assertEqual(
            form.config_field('indus_pack_field','IND'),
            ((pack1.id, "{} /{}{}".format(pack1.brand, pack1.qt_paquet, pack1.unit)),
              (pack2.id, "{} /{}{}".format(pack2.brand, pack2.qt_paquet, pack2.unit)),)
            )
        self.assertEqual(
            form.initial['indus_pack_field'],
            (pack2.id, "{} /{}{}".format(pack2.brand, pack2.qt_paquet, pack2.unit))
            )
        pack3 = self.db_pack_rol
        self.assertEqual(
            form.config_field('rol_pack_field', 'ROL'),
            ((pack3.id, "{} /{}{}".format(pack3.brand, pack3.qt_paquet, pack3.unit)),)
            )
        pack4 = self.db_pack_nb
        self.assertEqual(
            form.config_field('nb_pack_field', 'NB'),
            ((pack4.id, "{} /{}{}".format(pack4.brand, pack4.qt_paquet, pack4.unit)),)
        )
        self.assertEqual(form.config_field('gr_pack_field', 'GR'), ())
