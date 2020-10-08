#!/usr/bin/env python
# pylint: disable=R0902 #Too many instance attributes (12/7) (too-many-instance-attributes)
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code


""" tests on models.py """
import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophy
)


class TestModels(TestCase):
    """test models.py with a TestCase class"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.usertestprofile = UserProfile.objects.create(
            user=self.usertest,
            date_start=datetime.date(2020, 5, 13),
            starting_nb_cig=20)
        self.paquet = Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        self.paquet2 = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='1637',
            qt_paquet=30,
            price=12,
            )
        self.consocig = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 13, 55, tzinfo=pytz.utc),
            paquet=self.paquet,
        )
        self.consocig2 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 0, 0, tzinfo=pytz.utc),
            given=True,
        )
        self.alternative = Alternative.objects.create(
            user=self.usertest,
            type_activity='Sp',
            activity='VELO',
        )
        self.alternative2 = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='PAST',
            nicotine=2,
        )
        self.consoalter = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 11, 5, tzinfo=pytz.utc),
            alternative=self.alternative2
        )
        self.consoalter2 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 14, 15, tzinfo=pytz.utc),
            alternative=self.alternative,
            activity_duration=75,
        )
        self.objectif = Objectif.objects.create(
            user=self.usertest,
            qt=15,
            datetime_creation= make_aware(datetime.datetime(2020, 5, 17, 14, 30)),
            datetime_objectif=make_aware(datetime.datetime(2020, 7, 17, 14, 30)),
        )
        self.trophy = Trophy.objects.create(
            user=self.usertest,
            nb_cig=20,
            nb_jour=3,
        )

    def test_user_model(self):
        """test user object creation"""
        self.assertTrue(User.objects.filter(username="arandomname").exists())
        self.assertTrue(User.objects.get(username="arandomname").check_password('arandompassword'))

    def test_userprofile_model(self):
        """test userprofile object creation"""
        self.assertTrue(UserProfile.objects.filter(user=self.usertest).exists())
        self.assertEqual(UserProfile.objects.get(user=self.usertest).starting_nb_cig, 20)

    def test_paquet_model(self):
        """test paquet object creation"""
        self.assertTrue(Paquet.objects.filter(user=self.usertest).exists())
        self.assertEqual(Paquet.objects.filter(user=self.usertest).count(), 2)
        self.assertEqual(self.paquet.type_cig, 'IND')
        self.assertEqual(self.paquet2.type_cig, 'ROL')
        self.assertEqual(str(self.paquet), 'IND CAMEL 20U')

    def test_consocig_model(self):
        """ test conso cig creation"""
        self.assertTrue(ConsoCig.objects.filter(user=self.usertest).exists())
        self.assertEqual(ConsoCig.objects.filter(user=self.usertest).count(), 2)
        self.assertEqual(ConsoCig.objects.filter(user=self.usertest, paquet=self.paquet).count(), 1)
        self.assertEqual(str(self.consocig2), 'arandomname 2020-05-13 00:00:00+00:00-None')
        self.assertEqual(str(self.consocig), 'arandomname 2020-05-13 13:55:00+00:00-IND')

    def test_alternative_model(self):
        """ test alternative creation"""
        self.assertTrue(Alternative.objects.filter(user=self.usertest).exists())
        self.assertEqual(Alternative.objects.filter(user=self.usertest).count(), 2)
        self.assertEqual(Alternative.objects.filter(
            user=self.usertest, type_alternative='Su').count(), 1)

    def test_alternative_model_double(self):
        """ test alternative creation"""
        Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='PAST',
            nicotine=3,
        )
        self.assertTrue(Alternative.objects.filter(user=self.usertest).exists())
        self.assertEqual(Alternative.objects.filter(
            user=self.usertest).count(), 3)
        self.assertEqual(Alternative.objects.filter(
            user=self.usertest, type_alternative='Su').count(), 2)


    def test_consoalter_model(self):
        """ test conso alternative creation"""
        self.assertTrue(ConsoAlternative.objects.filter(user=self.usertest).exists())
        self.assertEqual(ConsoAlternative.objects.filter(user=self.usertest).count(), 2)
        self.assertEqual(ConsoAlternative.objects.filter(
            user=self.usertest, alternative=self.alternative).count(), 1)

    def test_objectif_model(self):
        """ test objectif creation"""
        self.assertTrue(Objectif.objects.filter(user=self.usertest).exists())

    def test_trophy_model(self):
        """ test trophhe creation"""
        self.assertTrue(Trophy.objects.filter(user=self.usertest).exists())
