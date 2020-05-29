#!/usr/bin/env python

import datetime

from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from QuitSoonApp.forms import HealthForm
from QuitSoonApp.models import Alternative, ConsoAlternative


class Test_HealthForm(TestCase):

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")
        self.db_alternative_undisplayed = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Lo',
            activity='DESSIN',
            display=False,
            )
        self.db_alternative_substitut_ecig = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='ecig',
            nicotine=3,
            display=True,
            )
        self.db_alternative_activity_sp = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            display=True,
            )

        self.db_alternative_activity_so = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='TABACOLOGUE',
            display=True,
            )
        self.db_alternative_activity_so2 = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='MASSAGE',
            display=True,
            )
        self.db_alternative_substitut_p24 = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='P24',
            nicotine=2,
            display=True,
            )
        self.db_alternative_substitut_past = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='PAST',
            nicotine=3,
            display=True,
            )

        self.conso_1 = ConsoAlternative.objects.create(
            user=self.usertest,
            date_alter=datetime.date(2020, 5, 13),
            time_alter=datetime.time(13, 55),
            alternative=self.db_alternative_activity_so,
        )
        self.conso_2 = ConsoAlternative.objects.create(
            user=self.usertest,
            date_alter=datetime.date(2020, 6, 13),
            time_alter=datetime.time(13, 55),
            alternative=self.db_alternative_substitut_past,
        )
        self.conso_3 = ConsoAlternative.objects.create(
            user=self.usertest,
            date_alter=datetime.date(2020, 5, 13),
            time_alter=datetime.time(14, 55),
            alternative=self.db_alternative_substitut_p24,
        )
        self.conso_4 = ConsoAlternative.objects.create(
            user=self.usertest,
            date_alter=datetime.date(2020, 6, 14),
            time_alter=datetime.time(13, 55),
            alternative=self.db_alternative_activity_sp,
        )
        self.conso_5 = ConsoAlternative.objects.create(
            user=self.usertest,
            date_alter=datetime.date(2020, 7, 13),
            time_alter=datetime.time(13, 55),
            alternative=self.db_alternative_activity_so2,
        )

class test_HealthForm_field_config(Test_HealthForm):

    def test_last_alternative(self):
        form = HealthForm(self.usertest)
        self.assertEqual(form.last_alternative().type_activity, 'So')
        self.assertEqual(form.last_alternative('Su').substitut, 'P24')
        self.assertEqual(form.last_alternative('Ac', 'Sp').activity, 'COURSE')
        self.assertEqual(form.last_alternative('Ac', 'So').activity, 'MASSAGE')
        self.assertEqual(form.last_alternative('Ac', 'Lo'), None)

    def test_choices_type_alternative(self):
        form = HealthForm(self.usertest)
        self.assertEqual(form.initial['type_alternative_field'][0], 'So')
        self.assertEqual(len(form.fields['type_alternative_field'].choices), 3)

    def test_choices_sp_field(self):
        form = HealthForm(self.usertest)
        self.assertEqual(form.initial['sp_field'][0], self.db_alternative_activity_sp.id)
        self.assertEqual(len(form.fields['sp_field'].choices), 1)
        self.assertEqual(form.fields['sp_field'].choices[0][0], self.db_alternative_activity_sp.id)

    def test_choices_so_field(self):
        form = HealthForm(self.usertest)
        self.assertEqual(form.initial['so_field'][0], self.db_alternative_activity_so2.id)
        self.assertEqual(len(form.fields['so_field'].choices), 2)

    def test_choices_lo_field(self):
        form = HealthForm(self.usertest)
        try:
            self.assertTrue(form.initial['lo_field'])
        except Exception:
            self.assertRaises(KeyError)
        self.assertEqual(len(form.fields['lo_field'].choices), 0)

    def test_choices_su_field(self):
        form = HealthForm(self.usertest)
        self.assertEqual(form.initial['su_field'][0], self.db_alternative_substitut_p24.id)
        self.assertEqual(len(form.fields['su_field'].choices), 3)

    def test_choices_first_health(self):
        ConsoAlternative.objects.all().delete()
        self.assertEqual(ConsoAlternative.objects.count(), 0)
        form = HealthForm(self.usertest)
        self.assertEqual(form.last_alternative().type_alternative, 'Su')
        self.assertEqual(form.last_alternative('Su').substitut, 'PAST')
        self.assertEqual(form.last_alternative('Ac', 'Sp').activity, 'COURSE')
        self.assertEqual(form.last_alternative('Ac', 'So').activity, 'MASSAGE')
        self.assertEqual(form.last_alternative('Ac', 'Lo'), None)
        self.assertEqual(form.initial['type_alternative_field'][0], 'Su')
        self.assertEqual(form.initial['sp_field'][0], self.db_alternative_activity_sp.id)
        self.assertEqual(form.initial['so_field'][0], self.db_alternative_activity_so2.id)
        self.assertEqual(form.initial['su_field'][0], self.db_alternative_substitut_past.id)

class Test_HealthForm_validation_data(Test_HealthForm):

    def test_valid_data(self):
        data = {
            'date_health':datetime.date(2020, 5, 26),
            'time_health':datetime.time(12, 56),
            'duration_hour':1,
            'duration_min':30,
            'type_alternative_field':'So',
            'sp_field':self.db_alternative_activity_sp.id,
            'so_field':self.db_alternative_activity_so.id,
            'su_field':self.db_alternative_substitut_p24.id,
        }
        form = HealthForm(self.usertest, data)
        self.assertTrue(form.is_valid())

    def test_required_fields(self):
        form = HealthForm(self.usertest, {})
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)
        self.assertEqual(form.errors, {
            'date_health': ['Ce champ est obligatoire.'],
            'time_health': ['Ce champ est obligatoire.'],
            'type_alternative_field': ['Ce champ est obligatoire.'],
            '__all__':["Vous n'avez pas renseigné de durée pour cette activité"],
            })


    def test_duration_0(self):
        data = {
            'date_health':datetime.date(2020, 5, 26),
            'time_health':datetime.time(12, 56),
            'duration_hour':0,
            'duration_min':0,
            'type_alternative_field':'So',
            'sp_field':self.db_alternative_activity_sp.id,
            'so_field':self.db_alternative_activity_so.id,
            'su_field':self.db_alternative_substitut_p24.id,
        }
        form = HealthForm(self.usertest, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)
        self.assertEqual(form.errors, {
            '__all__':["Vous n'avez pas renseigné de durée pour cette activité"],
            })

class Test_HealthForm_ECIG(TestCase):

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")
        self.db_alternative_undisplayed = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Lo',
            activity='DESSIN',
            display=False,
            )
        self.db_alternative_substitut_ecig = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='ecig',
            nicotine=3,
            display=True,
            )

    def test_get_ecig_none(self):
        data = {
            'date_health':datetime.date(2020, 5, 26),
            'time_health':datetime.time(12, 56),
            'type_alternative_field':'Su',
            'su_field':self.db_alternative_substitut_ecig.id,
            'ecig_vape_or_start':[]
        }
        form = HealthForm(self.usertest, data)
        self.assertFalse(form.is_valid())
        self.assertTrue("Vous avez sélectionné la cigarette électronique" in form.errors['__all__'][0])
