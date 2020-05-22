from decimal import Decimal
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
    profile, new_name, new_email, new_password, new_parameters,
    suivi, objectifs,
    paquets, bad, bad_history,
    alternatives, good, good_history,
)
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)
from QuitSoonApp.modules.save_pack import SavePack


class SavePackTestCase(TestCase):

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2012-12-12',
            starting_nb_cig=3
        )

    def test_get_unit_u(self):
        """test SavePack.get_unit method if type_cig == IND"""
        datas ={
            'type_cig':'IND',
            'brand':'Camel',
            'qt_paquet':20,
            'price':10,
            }
        pack = SavePack(self.usertest, datas)
        self.assertEqual(pack.get_unit, 'U')
        self.assertEqual(pack.unit, 'U')

    def test_get_unit_g(self):
        """test SavePack.get_unit method if type_cig == ROL"""
        datas ={
            'type_cig':'ROL',
            'brand':'1637',
            'qt_paquet':30,
            'price':11,
            }
        pack = SavePack(self.usertest, datas)
        self.assertEqual(pack.get_unit, 'G')
        self.assertEqual(pack.unit, 'G')

    def test_get_initial_g_per_cig_u(self):
        """test SavePack.get_g_per_cig method when create new pack & if type_cig == 'IND'"""
        datas ={
            'type_cig':'IND',
            'brand':'Camel',
            'qt_paquet':20,
            'price':10,
            }
        pack = SavePack(self.usertest, datas)
        self.assertEqual(pack.get_g_per_cig(), None)
        self.assertEqual(pack.g_per_cig, None)

    def test_get_initial_g_per_cig_g(self):
        """test SavePack.get_g_per_cig method when create new pack & if type_cig == 'ROL'"""
        datas ={
            'type_cig':'ROL',
            'brand':'1637',
            'qt_paquet':30,
            'price':11,
            }
        pack = SavePack(self.usertest, datas)
        self.assertEqual(pack.get_g_per_cig(), 0.8)
        self.assertEqual(pack.g_per_cig, 0.8)

    def test_get_new_g_per_cig(self):
        """test SavePack.get_g_per_cig method when create new pack & if type_cig == 'ROL'"""
        datas ={
            'type_cig':'ROL',
            'brand':'1637',
            'qt_paquet':30,
            'price':11,
            'g_per_cig':0.9
            }
        pack = SavePack(self.usertest, datas)
        self.assertEqual(pack.get_g_per_cig(datas['g_per_cig']), 0.9)
        self.assertEqual(pack.g_per_cig, 0.9)

    def tes_get_price_per_cig_u(self):
        """test SavePack.get_price_per_cig method if type_cig == 'IND'"""
        datas ={
            'type_cig':'IND',
            'brand':'Camel',
            'qt_paquet':20,
            'price':10,
        }
        pack = SavePack(self.usertest, datas)
        self.assertEqual(pack.get_price_per_cig, 0.5)
        self.assertEqual(pack.price_per_cig, 0.5)

    def tes_get_price_per_cig_gr(self):
        """test SavePack.get_price_per_cig method if type_cig == 'IND'"""
        datas ={
            'type_cig':'ROL',
            'brand':'1637',
            'qt_paquet':30,
            'price':11,
            }
        pack = SavePack(self.usertest, datas)
        self.assertEqual(pack.get_price_per_cig, 0.29)
        self.assertEqual(pack.price_per_cig, 0.29)

    def test_create_new_pack_ind(self):
        """test SavePack.create_pack method if type_cig == 'IND'"""
        datas ={
            'type_cig':'IND',
            'brand':'CAMEL',
            'qt_paquet':20,
            'price':10,
            }
        pack = SavePack(self.usertest, datas)
        pack.create_pack()
        db_pack = Paquet.objects.filter(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        self.assertTrue(db_pack.exists())
        self.assertEqual(db_pack[0].unit, 'U')
        self.assertEqual(db_pack[0].g_per_cig, None)
        self.assertEqual(db_pack[0].price_per_cig, 0.5)

    def test_create_new_pack_gr(self):
        """test SavePack.create_pack method if type_cig == 'GR'"""
        datas ={
            'type_cig':'GR',
            'brand':'TEST AUTRE',
            'qt_paquet':50,
            'price':30,
            }
        pack = SavePack(self.usertest, datas)
        pack.create_pack()
        db_pack = Paquet.objects.filter(
            user=self.usertest,
            type_cig='GR',
            brand='TEST AUTRE',
            qt_paquet=50,
            price=30,
            )
        self.assertTrue(db_pack.exists())
        self.assertEqual(db_pack[0].unit, 'G')
        self.assertEqual(db_pack[0].g_per_cig, Decimal('0.8'))
        self.assertEqual(db_pack[0].price_per_cig, Decimal('0.48'))

    def test_create_pack_already_in_db(self):
        """test SavePack.create_pack method if type_cig == 'GR'"""
        db_pack = Paquet.objects.filter(
            user=self.usertest,
            type_cig='GR',
            brand='TEST AUTRE',
            qt_paquet=50,
            price=30,
            display=False,
            )
        datas ={
            'type_cig':'GR',
            'brand':'TEST AUTRE',
            'qt_paquet':50,
            'price':30,
            }
        pack = SavePack(self.usertest, datas)
        pack.create_pack()
        db_pack = Paquet.objects.filter(
            user=self.usertest,
            type_cig='GR',
            brand='TEST AUTRE',
            qt_paquet=50,
            price=30,
            )
        self.assertFalse(db_pack.count() == 2)
        self.assertEqual(db_pack.count(), 1)
        self.assertEqual(db_pack[0].display, True)

    def test_delete_unused_pack_ind(self):
        """test SavePack.delete_pack method with unused pack"""
        Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        datas ={
            'type_cig':'IND',
            'brand':'CAMEL',
            'qt_paquet':20,
            'price':10,
            }
        pack = SavePack(self.usertest, datas)
        pack.delete_pack()
        db_pack = Paquet.objects.filter(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        self.assertFalse(db_pack.exists())

    def test_delete_used_pack_ind(self):
        """test SavePack.delete_pack method with used pack"""
        pack = Paquet.objects.create(
            user=self.usertest,
            type_cig='CIGARIOS',
            brand='ELPASO',
            qt_paquet=5,
            price=10,
            )
        ConsoCig.objects.create(
            user=self.usertest,
            date_cig=datetime.date(2020, 5, 13),
            time_cig=datetime.time(13, 55),
            paquet=pack,
        )
        datas ={
            'type_cig':'CIGARIOS',
            'brand':'ELPASO',
            'qt_paquet':5,
            'price':10,
            }
        pack = SavePack(self.usertest, datas)
        pack.delete_pack()
        db_pack = Paquet.objects.filter(
            user=self.usertest,
            type_cig='CIGARIOS',
            brand='ELPASO',
            qt_paquet=5,
            price=10,
            )
        self.assertTrue(db_pack.exists())
        self.assertEqual(db_pack[0].display, False)

    def test_update_pack_g_per_cig(self):
        """test SavePack.update_pack_g_per_cig method"""
        paquet = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='TABACO',
            qt_paquet=40,
            price=15,
            g_per_cig=0.8,
            price_per_cig=0.3
            )
        self.assertEqual(paquet.g_per_cig, 0.8)
        self.assertEqual(paquet.price_per_cig, 0.3)
        datas ={
            'type_cig':'ROL',
            'brand':'TABACO',
            'qt_paquet':40,
            'price':15,
            'g_per_cig':0.6
            }
        pack = SavePack(self.usertest, datas)
        pack.update_pack_g_per_cig()
        find_pack = Paquet.objects.get(
            id=paquet.id,
        )
        self.assertEqual(find_pack.g_per_cig, Decimal('0.6'))
        self.assertEqual(find_pack.price_per_cig, Decimal('0.22'))
