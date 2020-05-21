import datetime

from django.test import TransactionTestCase, TestCase
from django.utils.timezone import make_aware
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from QuitSoonApp.views import (
    index, today,
    register_view, login_view,
    profile, paquets, alternatives,
    suivi, objectifs
)
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)
from QuitSoonApp.modules.resetprofile import ResetProfile


class ResetProfileTestCase(TestCase):

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2012-12-12',
            starting_nb_cig=3
        )
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

    def test_reset_profile(self):
        self.assertTrue(UserProfile.objects.filter(user=self.usertest).exists())
        userprofile = ResetProfile(self.usertest, {'date_start':'2020-05-15', 'starting_nb_cig':20})
        self.assertFalse(UserProfile.objects.filter(user=self.usertest).exists())
        self.assertTrue(Paquet.objects.filter(user=self.usertest).exists())
        self.assertTrue(Alternative.objects.filter(user=self.usertest).exists())
        self.assertFalse(ConsoCig.objects.filter(user=self.usertest).exists())
        self.assertFalse(ConsoAlternative.objects.filter(user=self.usertest).exists())
        self.assertFalse(Objectif.objects.filter(user=self.usertest).exists())
        self.assertFalse(Trophee.objects.filter(user=self.usertest).exists())

    def test_new_profile(self):
        userprofile = ResetProfile(self.usertest, {'date_start':'2020-05-15', 'starting_nb_cig':20})
        userprofile.new_profile()
        self.assertTrue(UserProfile.objects.filter(user=self.usertest).exists())
        self.assertEqual(UserProfile.objects.get(user=self.usertest).date_start, datetime.date(2020, 5, 15))
        self.assertEqual(UserProfile.objects.get(user=self.usertest).starting_nb_cig, 20)
