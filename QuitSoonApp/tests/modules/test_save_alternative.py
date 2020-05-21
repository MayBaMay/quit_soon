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
from QuitSoonApp.modules.save_alternative import SaveAlternative

class SavePackTestCase(TestCase):

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')

    def test_create_new_alternative(self):
        """test SavePack.create_alternative method if type_alternative != 'Su'"""
        datas ={
            'type_alternative':'Ac',
            'type_activity':'Sp',
            'activity': 'COURSE',
            }
        alternative = SaveAlternative(self.usertest, datas)
        alternative.create_alternative()
        db_create_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            )
        self.assertTrue(db_create_alternative.exists())

    def test_create_new_alternative_substitut(self):
        """test SavePack.create_alternative method if type_alternative == 'Su'"""
        datas ={
            'type_alternative':'Su',
            'substitut':'P24',
            'nicotine': 2,
            }
        alternative = SaveAlternative(self.usertest, datas)
        alternative.create_alternative()
        db_create_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='P24',
            nicotine=2.0,
            )
        self.assertTrue(db_create_alternative.exists())

    # def test_delete_unused_pack_ind(self):
    #     """test SavePack.delete_pack method with unused pack"""
    #     Paquet.objects.create(
    #         user=self.usertest,
    #         type_cig='IND',
    #         brand='CAMEL',
    #         qt_paquet=20,
    #         price=10,
    #         )
    #     datas ={
    #         'type_cig':'IND',
    #         'brand':'CAMEL',
    #         'qt_paquet':20,
    #         'price':10,
    #         }
    #     pack = SavePack(self.usertest, datas)
    #     pack.delete_pack()
    #     db_pack = Paquet.objects.filter(
    #         user=self.usertest,
    #         type_cig='IND',
    #         brand='CAMEL',
    #         qt_paquet=20,
    #         price=10,
    #         )
    #     self.assertFalse(db_pack.exists())
    #
    # def test_delete_used_pack_ind(self):
    #     """test SavePack.delete_pack method with used pack"""
    #     pack = Paquet.objects.create(
    #         user=self.usertest,
    #         type_cig='CIGARIOS',
    #         brand='ELPASO',
    #         qt_paquet=5,
    #         price=10,
    #         )
    #     ConsoCig.objects.create(
    #         user=self.usertest,
    #         date_cig=datetime.date(2020, 5, 13),
    #         time_cig=datetime.time(13, 55),
    #         paquet=pack,
    #     )
    #     datas ={
    #         'type_cig':'CIGARIOS',
    #         'brand':'ELPASO',
    #         'qt_paquet':5,
    #         'price':10,
    #         }
    #     pack = SavePack(self.usertest, datas)
    #     pack.delete_pack()
    #     db_pack = Paquet.objects.filter(
    #         user=self.usertest,
    #         type_cig='CIGARIOS',
    #         brand='ELPASO',
    #         qt_paquet=5,
    #         price=10,
    #         )
    #     self.assertTrue(db_pack.exists())
    #     self.assertEqual(db_pack[0].display, False)
    #
    # def test_update_pack_g_per_cig(self):
    #     """test SavePack.update_pack_g_per_cig method"""
    #     paquet = Paquet.objects.create(
    #         user=self.usertest,
    #         type_cig='ROL',
    #         brand='TABACO',
    #         qt_paquet=40,
    #         price=15,
    #         )
    #     self.assertEqual(paquet.g_per_cig, None)
    #     datas ={
    #         'type_cig':'ROL',
    #         'brand':'TABACO',
    #         'qt_paquet':40,
    #         'price':15,
    #         'g_per_cig':0.6
    #         }
    #     pack = SavePack(self.usertest, datas)
    #     pack.update_pack_g_per_cig()
    #     find_pack = Paquet.objects.get(
    #         id=paquet.id,
    #     )
    #     self.assertEqual(find_pack.g_per_cig, Decimal('0.6'))
