""" Single creation in test database """

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import Paquet, ConsoCig


class BaseTestCase(TestCase):

    def setUp(self):
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    #####   Packs ######

    @property
    def lucky(self):
        return Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='LUCKY',
            qt_paquet=20,
            price=10,
            display=False
            )

    @property
    def camel(self):
        return Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )

    @property
    def philip_morris(self):
        return Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='PHILIP MORRIS',
            qt_paquet=20,
            price=10.2,
            )

    @property
    def rol_1637(self):
        return Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='1637',
            qt_paquet=30,
            price=12,
            )

    @property
    def beedies(self):
        return Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='BEEDIES',
            qt_paquet=30,
            price=5,
            )

    @property
    def create_pack(self):
        return Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )


    @property
    def filter_pack_camel(self):
        return Paquet.objects.filter(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            first=True,
            )

    @property
    def filter_pack_brandtest(self):
        return Paquet.objects.filter(
            user=self.usertest,
            type_cig='ROL',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )

class BaseAllPacksTestCase(BaseTestCase):

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.db_pack_undisplayed = self.lucky
        self.db_pack_ind = self.camel
        self.db_pack_ind2 = self.philip_morris
        self.db_pack_rol = self.rol_1637
        self.db_pack_nb = self.beedies
