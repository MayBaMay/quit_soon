import datetime
import pytz

from django.test import TestCase
from django.utils.timezone import make_aware
from django.contrib.auth.models import User

from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophy
)
from QuitSoonApp.modules.profile_manager import ProfileManager
from ..MOCK_DATA import BaseTestCase


class ResetProfileTestCase(BaseTestCase):

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.paquet = Paquet.objects.create(
            user=self.usertest,
            brand='CAMEL',
            price=9.7,
            first=True,
            )
        self.paquet2 = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            qt_paquet=30,
            unit='G',
            brand='1637',
            price=11.5,
            g_per_cig=0.8,
            )
        self.oldpaquet = Paquet.objects.create(
            user=self.usertest,
            brand='CLOPE',
            price=9.7,
            display=False,
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
            display=False,
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

    def test_get_request_data(self):
        userprofile = ProfileManager(self.usertest, {})
        self.assertIsNone(userprofile.date_start)
        self.assertRaises(KeyError, userprofile.get_request_data('date_start'))

    def test_clean_old_datas(self):
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2012-12-12',
            starting_nb_cig=3
        )
        self.assertTrue(UserProfile.objects.filter(user=self.usertest).exists())
        userprofile = ProfileManager(self.usertest, {'date_start':'2020-05-15', 'starting_nb_cig':20, 'ref_pack':self.paquet2.id})
        self.assertFalse(UserProfile.objects.filter(user=self.usertest).exists())
        self.assertTrue(Paquet.objects.filter(user=self.usertest).exists())
        self.assertFalse(Paquet.objects.filter(user=self.usertest, first=True).exists())
        self.assertFalse(Paquet.objects.filter(user=self.usertest, display=False).exists())
        self.assertTrue(Alternative.objects.filter(user=self.usertest).exists())
        self.assertFalse(Alternative.objects.filter(user=self.usertest, display=False).exists())
        self.assertFalse(ConsoCig.objects.filter(user=self.usertest).exists())
        self.assertFalse(ConsoAlternative.objects.filter(user=self.usertest).exists())
        self.assertFalse(Objectif.objects.filter(user=self.usertest).exists())
        self.assertFalse(Trophy.objects.filter(user=self.usertest).exists())


    def test_new_profile(self):
        userprofile = ProfileManager(self.usertest, {'date_start':'2020-05-15', 'starting_nb_cig':20, 'ref_pack':self.paquet2.id})
        userprofile.new_profile()
        self.assertTrue(UserProfile.objects.filter(user=self.usertest).exists())
        self.assertEqual(UserProfile.objects.get(user=self.usertest).date_start, datetime.date(2020, 5, 15))
        self.assertEqual(UserProfile.objects.get(user=self.usertest).starting_nb_cig, 20)
        self.assertTrue(Paquet.objects.get(user=self.usertest, first=True).id, self.paquet2.id)
        self.assertTrue(Paquet.objects.filter(user=self.usertest, first=True).count(), 1)

    def test_reset_profile(self):
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2012-12-12',
            starting_nb_cig=3
        )
        userprofile = ProfileManager(self.usertest, {'date_start':'2020-05-15', 'starting_nb_cig':20, 'ref_pack':self.paquet2.id})
        userprofile.new_profile()
        self.assertTrue(UserProfile.objects.filter(user=self.usertest).exists())
        self.assertEqual(UserProfile.objects.get(user=self.usertest).date_start, datetime.date(2020, 5, 15))
        self.assertEqual(UserProfile.objects.get(user=self.usertest).starting_nb_cig, 20)
        self.assertTrue(Paquet.objects.get(user=self.usertest, first=True).id, self.paquet2.id)
        self.assertTrue(Paquet.objects.filter(user=self.usertest, first=True).count(), 1)
