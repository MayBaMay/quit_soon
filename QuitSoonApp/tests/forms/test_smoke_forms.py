#!/usr/bin/env python
# pylint: disable=C0103 #Method name "test_smokeForm_is_valid" doesn't conform to snake_case naming style (invalid-name)
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code


"""test Forms related to ConsoCig model"""

import datetime
import pytz
from freezegun import freeze_time

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from QuitSoonApp.forms import SmokeForm
from QuitSoonApp.models import Paquet, ConsoCig


class SmokeFormTestCase(TestCase):
    """Test SmokeForm"""

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
        self.valid_smoking_datas = {
            'date_smoke':datetime.date(2020, 5, 11),
            'time_smoke':datetime.time(12, 56),
            'type_cig_field':'IND',
            'ind_pack_field':self.db_pack_ind.id,
            'rol_pack_field':self.db_pack_rol.id,
            'given_field':False,
            }

    def test_smokeForm_is_valid(self):
        """test valid SmokeForm"""
        form = SmokeForm(self.usertest, -120,  self.valid_smoking_datas)
        self.assertTrue(form.is_valid())

    def test_smokeForm_is_not_valid(self):
        """test invalid SmokeForm, data missing"""
        form = SmokeForm(self.usertest, -120,  {})
        self.assertFalse(form.is_valid())
        for error in form.errors:
            print(error)
        self.assertEqual(form.errors, {
            'date_smoke': ['Ce champ est obligatoire.'],
            'time_smoke': ['Ce champ est obligatoire.'],
            'type_cig_field': ['Ce champ est obligatoire.'],
            '__all__':["Données temporelles incorrectes"]
            })

    @freeze_time("2020-06-17 23:59:59", tz_offset=+2)
    def test_clean_inf_today(self):
        """Function testing if form is invalide for days after today"""
        data = {
            'date_smoke':datetime.date(2020, 6, 18),
            'time_smoke':datetime.time(00, 21),
            'type_cig_field':'IND',
            'ind_pack_field':self.db_pack_ind.id,
            'rol_pack_field':self.db_pack_rol.id,
            'nb_pack_field':self.db_pack_nb.id,
            'given_field':False,
            }
        form = SmokeForm(self.usertest, -120, data)
        self.assertTrue(form.is_valid())


    @freeze_time("2020-06-17 23:59:59", tz_offset=+2)
    def test_clean_gt_today(self):
        """Function testing if form is invalide for days after today"""
        data = {
            'date_smoke':datetime.date(2020, 6, 18),
            'time_smoke':datetime.time(3, 21),
            'type_cig_field':'IND',
            'ind_pack_field':self.db_pack_ind.id,
            'rol_pack_field':self.db_pack_rol.id,
            'nb_pack_field':self.db_pack_nb.id,
            'given_field':False,
            }
        form = SmokeForm(self.usertest, -120, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)
        self.assertEqual(form.errors, {
            '__all__':["Vous ne pouvez pas enregistrer de craquage pour les jours à venir"],
            })

    def test_last_smoke_first_smoke(self):
        """ test last_smoke method first user ConsoCig"""
        form = SmokeForm(self.usertest, -120,  self.valid_smoking_datas)
        self.assertEqual(form.last_smoke, self.db_pack_nb)

    def test_smoke_last_none_first_smoke(self):
        """ test last_smoke method with last smoke given=False smoke """
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 17, 13, 15, tzinfo=pytz.utc),
            paquet=self.db_pack_ind2,
            )
        form = SmokeForm(self.usertest, -120)
        self.assertEqual(form.last_smoke, self.db_pack_ind2)

    def test_last_smoke_only_given(self):
        """ test get last paquet while user only smoked given cig """
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 16, 10, 15, tzinfo=pytz.utc),
            paquet=None,
            )
        form = SmokeForm(self.usertest, -120)
        self.assertEqual(form.last_smoke, self.db_pack_nb)

    def test_smoke_last_none(self):
        """ test last_smoke method with last one given=True, before exists given=False """
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 16, 10, 15, tzinfo=pytz.utc),
            paquet=self.db_pack_nb,
            )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 17, 10, 15, tzinfo=pytz.utc),
            paquet=self.db_pack_ind2,
            )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 17, 13, 15, tzinfo=pytz.utc),
            paquet=None,
            )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 17, 13, 15, tzinfo=pytz.utc),
            paquet=None,
            )
        form = SmokeForm(self.usertest, -120,  self.valid_smoking_datas)
        self.assertEqual(form.last_smoke, self.db_pack_ind2)

    def test_config_field(self):
        """ test config_field method """
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 17, 10, 15, tzinfo=pytz.utc),
            paquet=self.db_pack_ind2,
            )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 17, 13, 15, tzinfo=pytz.utc),
            given=True,
            )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 17, 13, 15, tzinfo=pytz.utc),
            given=True,
            )
        form = SmokeForm(self.usertest, -120,  self.valid_smoking_datas)
        pack1 = self.db_pack_ind
        pack2 = self.db_pack_ind2
        pack3 = self.db_pack_nb
        self.assertTrue(
            (pack1.id,
             "{} /{}{}".format(
                 pack1.brand,
                 pack1.qt_paquet,
                 pack1.unit)
             ) in form.config_field('ind_pack_field','IND')
            )
        self.assertTrue(
            (pack2.id,
             "{} /{}{}".format(
                 pack2.brand,
                 pack2.qt_paquet,
                 pack2.unit)
             ) in form.config_field('ind_pack_field','IND')
            )
        self.assertTrue(
            (pack3.id,
             "{} /{}{}".format(
                 pack3.brand,
                 pack3.qt_paquet,
                 pack3.unit
                 )
             ) in form.config_field('ind_pack_field','IND')
            )
        self.assertEqual(
            form.initial['ind_pack_field'],
            (pack2.id,
             "{} /{}{}".format(pack2.brand, pack2.qt_paquet, pack2.unit)
             )
            )
        pack3 = self.db_pack_rol
        self.assertEqual(
            form.config_field('rol_pack_field', 'ROL'),
            ((pack3.id, "{} /{}{}".format(pack3.brand, pack3.qt_paquet, pack3.unit)),)
            )
