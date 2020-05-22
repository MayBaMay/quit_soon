""" tests on models.py """
import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.timezone import make_aware
from ..models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)

class TestModels(TestCase):
    """test models.py with a TestCase class"""

    def setUp(self):
        """set up TestCase"""

        self.usertest = User.objects.create(
            username="usertest",
            email="user@test.com",
            password="password")
        self.usertestprofile = UserProfile.objects.create(
            user=self.usertest,
            date_start=datetime.date(2020, 5, 13),
            starting_nb_cig=20)
        self.paquet = Paquet.objects.create(
            user=self.usertest,
            brand='CAMEL',
            price=9.7,
            )
        self.paquet2 = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            qt_paquet=30,
            unit='G',
            brand='1637',
            price=11.5,
            g_per_cig=0.8,
            display=False
            )
        self.consocig = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 5, 13),
            time_cig=datetime.time(13, 55),
            paquet=self.paquet,
        )
        self.consocig2 = ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 5, 13),
            time_cig=datetime.time(0, 0),
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
            date_alter=datetime.date(2020, 5, 13),
            time_alter=datetime.time(11, 5),
            alternative=self.alternative2
        )
        self.consoalter2 = ConsoAlternative.objects.create(
            user=self.usertest,
            date_alter=datetime.date(2020, 5, 13),
            time_alter=datetime.time(14, 15),
            alternative=self.alternative,
            duration=75,
        )
        self.objectif = Objectif.objects.create(
            user=self.usertest,
            qt=15,
            datetime_creation= make_aware(datetime.datetime(2020, 5, 17, 14, 30)),
            datetime_objectif=make_aware(datetime.datetime(2020, 7, 17, 14, 30)),
        )
        self.trophee = Trophee.objects.create(
            user=self.usertest,
            nb_cig=20,
            nb_jour=3,
        )

    def test_user_model(self):
        """test user object creation"""
        self.assertTrue(User.objects.filter(username="usertest").exists())
        self.assertEqual(User.objects.get(username="usertest").password, 'password')

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

    def test_consocig_model(self):
        """ test conso cig creation"""
        self.assertTrue(ConsoCig.objects.filter(user=self.usertest).exists())
        self.assertEqual(ConsoCig.objects.filter(user=self.usertest).count(), 2)
        self.assertEqual(ConsoCig.objects.filter(user=self.usertest, paquet=self.paquet).count(), 1)

    def test_alternative_model(self):
        """ test alternative creation"""
        self.assertTrue(Alternative.objects.filter(user=self.usertest).exists())
        self.assertEqual(Alternative.objects.filter(user=self.usertest).count(), 2)
        self.assertEqual(Alternative.objects.filter(user=self.usertest, type_alternative='Su').count(), 1)

    def test_alternative_model_double(self):
        """ test alternative creation"""
        self.alternative3 = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='PAST',
            nicotine=3,
        )
        self.assertTrue(Alternative.objects.filter(user=self.usertest).exists())
        self.assertEqual(Alternative.objects.filter(user=self.usertest).count(), 3)
        self.assertEqual(Alternative.objects.filter(user=self.usertest, type_alternative='Su').count(), 2)


    def test_consoalter_model(self):
        """ test conso alternative creation"""
        self.assertTrue(ConsoAlternative.objects.filter(user=self.usertest).exists())
        self.assertEqual(ConsoAlternative.objects.filter(user=self.usertest).count(), 2)
        self.assertEqual(ConsoAlternative.objects.filter(user=self.usertest, alternative=self.alternative).count(), 1)

    def test_objectif_model(self):
        """ test objectif creation"""
        self.assertTrue(Objectif.objects.filter(user=self.usertest).exists())

    def test_trophee_model(self):
        """ test trophhe creation"""
        self.assertTrue(Trophee.objects.filter(user=self.usertest).exists())
