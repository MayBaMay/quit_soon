from decimal import Decimal
import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import Alternative, ConsoAlternative
from QuitSoonApp.modules import AlternativeManager
from ..MOCK_DATA import BaseTestCase

class SavePackTestCase(BaseTestCase):

    def setUp(self):
        """setup tests"""
        super().setUp()

    def test_get_request_data(self):
        """test method get_request_data"""
        data ={
            'type_alternative':'Su',
            'substitut':'P24',
            'nicotine': 2,
            }
        alternative = AlternativeManager(self.usertest, data)
        self.assertEqual(alternative.get_request_data('type_alternative'), 'Su')
        self.assertEqual(alternative.get_request_data('type_activity'), None)
        self.assertEqual(alternative.get_request_data('activity'), None)
        self.assertEqual(alternative.get_request_data('substitut'), 'P24')
        self.assertEqual(alternative.get_request_data('nicotine'), 2)

    def test_if_strNone_get_None_or_str(self):
        """test method get_str"""
        data = 'None'
        self.assertEqual(AlternativeManager.get_str(data), None)
        data = 1637
        self.assertEqual(AlternativeManager.get_str(data), '1637')
        data = 'Su'
        self.assertEqual(AlternativeManager.get_str(data), 'Su')

    def test_if_strNone_get_None_or_float(self):
        """test method str_get_float"""
        data = 'None'
        self.assertEqual(AlternativeManager.str_get_float(data), None)
        data = '2'
        self.assertEqual(AlternativeManager.str_get_float(data), 2.0)
        data = '2.0'
        self.assertEqual(AlternativeManager.str_get_float(data), 2.0)
        data = 'erreur'
        self.assertRaises(ValueError, AlternativeManager.str_get_float(data))
        self.assertEqual(AlternativeManager.str_get_float(data), None)

    def test_get_alternative(self):
        """test method get_alternative"""
        old = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            display=False,
            )

        data ={
            'type_alternative':'Ac',
            'type_activity':'Sp',
            'activity': 'COURSE',
            }
        alt = AlternativeManager(self.usertest, data)
        self.assertTrue(alt.get_alternative)

    def test_create_new_alternative(self):
        """test SavePack.create_alternative method if type_alternative != 'Su'"""
        data ={
            'type_alternative':'Ac',
            'type_activity':'Sp',
            'activity': 'COURSE',
            }
        alternative = AlternativeManager(self.usertest, data)
        alternative.create_alternative()
        db_create_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            )
        self.assertTrue(db_create_alternative.exists())

    def test_create_new_alternative_already_in_db(self):
        """test SavePack.create_alternative method if type_alternative == 'Su' and alternative already in db"""
        Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='P24',
            nicotine=2.0,
            display=False,
            )

        data ={
            'type_alternative':'Su',
            'substitut':'P24',
            'nicotine': 2,
            }
        alternative = AlternativeManager(self.usertest, data)
        alternative.create_alternative()
        db_create_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='P24',
            nicotine=2.0,
            )
        self.assertFalse(db_create_alternative.count() == 2)
        self.assertEqual(db_create_alternative.count(), 1)
        self.assertEqual(db_create_alternative[0].display, True)

    def test_create_new_alternative_substitut(self):
        """test SavePack.create_alternative method if type_alternative == 'Su'"""
        data ={
            'type_alternative':'Su',
            'substitut':'P24',
            'nicotine': 2,
            }
        alternative = AlternativeManager(self.usertest, data)
        alternative.create_alternative()
        db_create_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='P24',
            nicotine=2.0,
            )
        self.assertTrue(db_create_alternative.exists())

    def test_create_new_alternative_substitut_already_in_db(self):
        """test SavePack.create_alternative method if type_alternative == 'Su'"""
        Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='ECIG',
            nicotine=2.0,
            )
        data ={
            'type_alternative':'Su',
            'substitut':'ECIG',
            'nicotine': 2,
            }
        alternative = AlternativeManager(self.usertest, data)
        alternative.create_alternative()
        db_create_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='ECIG',
            nicotine=2.0,
            )
        self.assertFalse(db_create_alternative.count() == 2)

    def test_delete_unused_alternative_activity(self):
        """test AlternativeManager.delete_alternative method with unused alternative"""
        db_alternative = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='PSYCHOLOGUE',
            )
        data = {'id_alternative': db_alternative.id}
        alternative = AlternativeManager(self.usertest, data)
        alternative.delete_alternative()
        filter_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='PSYCHOLOGUE',
            )
        self.assertFalse(filter_alternative.exists())

    def test_delete_unused_alternative_substitut(self):
        """test AlternativeManager.delete_alternative method with unused alternative"""
        db_alternative = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='ECIG',
            nicotine=2.0,
            )
        data = {'id_alternative': db_alternative.id}
        alternative = AlternativeManager(self.usertest, data)
        alternative.delete_alternative()
        filter_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='ECIG',
            nicotine=2.0,
            )
        self.assertFalse(filter_alternative.exists())

    def test_delete_used_alternative_activity(self):
        """test SavePack.delete_alternative method with used alternative"""
        db_alternative = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='PSYCHOLOGUE',
            )
        conso = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 13, 55, tzinfo=pytz.utc),
            alternative=db_alternative,
        )
        data = {'id_alternative': db_alternative.id}
        alternative = AlternativeManager(self.usertest, data)
        alternative.delete_alternative()
        filter_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='PSYCHOLOGUE',
            )
        self.assertTrue(filter_alternative.exists())
        self.assertEqual(filter_alternative[0].display, False)

    def test_delete_used_alternative_substitut(self):
        """test SavePack.delete_alternative method with used alternative"""
        db_alternative = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='ECIG',
            nicotine=2.0,
            )
        conso = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 13, 55, tzinfo=pytz.utc),
            alternative=db_alternative,
        )
        data = {'id_alternative': db_alternative.id}
        alternative = AlternativeManager(self.usertest, data)
        alternative.delete_alternative()
        filter_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='ECIG',
            nicotine=2.0,
            )
        self.assertTrue(filter_alternative.exists())
        self.assertEqual(filter_alternative[0].display, False)
