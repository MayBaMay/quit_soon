#!/usr/bin/env python
# pylint: disable=R0902 #Too many instance attributes (12/7) (too-many-instance-attributes)
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code


"""test Forms related to ConsoAlternative model"""

import datetime
import pytz
from freezegun import freeze_time

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from QuitSoonApp.forms import HealthForm, ChooseAlternativeFormWithEmptyFields, ActivityForm
from QuitSoonApp.models import Alternative, ConsoAlternative


class ActivityFormTestCase(TestCase):
    """test ActivityForm"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_clean_activity(self):
        """test ActivityForm cleaning method"""
        data = {
            'type_activity':'Sp',
            'activity':'course',
        }
        form = ActivityForm(self.usertest, data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data.get('activity'), 'COURSE')


class HealthFormTestCase(TestCase):
    """Common attributs for HealthForm test's classes"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.db_alternative_undisplayed = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Lo',
            activity='DESSIN',
            display=False,
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
            datetime_alter=datetime.datetime(2020, 5, 13, 13, 55, tzinfo=pytz.utc),
            alternative=self.db_alternative_activity_so,
        )
        self.conso_2 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 6, 13, 13, 55, tzinfo=pytz.utc),
            alternative=self.db_alternative_substitut_past,
        )
        self.conso_3 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 14, 55, tzinfo=pytz.utc),
            alternative=self.db_alternative_substitut_p24,
        )
        self.conso_4 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 6, 14, 13, 55, tzinfo=pytz.utc),
            alternative=self.db_alternative_activity_sp,
        )
        self.conso_5 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 7, 13, 13, 55, tzinfo=pytz.utc),
            alternative=self.db_alternative_activity_so2,
        )


class HealthFormTestCaseFieldConfigTestCase(HealthFormTestCase):
    """test HealthForm field_configuration"""

    def test_last_alternative(self):
        """test HealthForm last_alternative method"""
        form = HealthForm(self.usertest, -120)
        self.assertEqual(form.last_alternative().type_activity, 'So')
        self.assertEqual(form.last_alternative('Su').substitut, 'P24')
        self.assertEqual(form.last_alternative('Ac', 'Sp').activity, 'COURSE')
        self.assertEqual(form.last_alternative('Ac', 'So').activity, 'MASSAGE')
        self.assertEqual(form.last_alternative('Ac', 'Lo'), None)

    def test_choices_type_alternative(self):
        """test HealthForm choices alternatiev field"""
        form = HealthForm(self.usertest, -120)
        self.assertEqual(form.initial['type_alternative_field'][0], 'So')
        self.assertEqual(len(form.fields['type_alternative_field'].choices), 3)

    def test_choices_sp_field(self):
        """test HealthForm choices 'sport' field"""
        form = HealthForm(self.usertest, -120)
        self.assertEqual(form.initial['sp_field'][0], self.db_alternative_activity_sp.id)
        self.assertEqual(len(form.fields['sp_field'].choices), 1)
        self.assertEqual(form.fields['sp_field'].choices[0][0], self.db_alternative_activity_sp.id)

    def test_choices_so_field(self):
        """test HealthForm choices 'soin' field"""
        form = HealthForm(self.usertest, -120)
        self.assertEqual(form.initial['so_field'][0], self.db_alternative_activity_so2.id)
        self.assertEqual(len(form.fields['so_field'].choices), 2)

    def test_choices_lo_field(self):
        """test HealthForm choices 'loisir' field"""
        form = HealthForm(self.usertest, -120)
        try:
            self.assertTrue(form.initial['lo_field'])
        except KeyError:
            self.assertRaises(KeyError)
        self.assertEqual(len(form.fields['lo_field'].choices), 0)

    def test_choices_su_field(self):
        """test HealthForm choices 'substitut' field"""
        form = HealthForm(self.usertest, -120)
        self.assertEqual(form.initial['su_field'][0], self.db_alternative_substitut_p24.id)
        self.assertEqual(len(form.fields['su_field'].choices), 2)

    def test_choices_first_health(self):
        """test HealthForm configuration initial field"""
        ConsoAlternative.objects.all().delete()
        self.assertEqual(ConsoAlternative.objects.count(), 0)
        form = HealthForm(self.usertest, -120)
        self.assertEqual(form.last_alternative().type_alternative, 'Su')
        self.assertEqual(form.last_alternative('Su').substitut, 'PAST')
        self.assertEqual(form.last_alternative('Ac', 'Sp').activity, 'COURSE')
        self.assertEqual(form.last_alternative('Ac', 'So').activity, 'MASSAGE')
        self.assertEqual(form.last_alternative('Ac', 'Lo'), None)
        self.assertEqual(form.initial['type_alternative_field'][0], 'Su')
        self.assertEqual(form.initial['sp_field'][0], self.db_alternative_activity_sp.id)
        self.assertEqual(form.initial['so_field'][0], self.db_alternative_activity_so2.id)
        self.assertEqual(form.initial['su_field'][0], self.db_alternative_substitut_past.id)


class HealthFormTestCaseValidationDataTestCase(HealthFormTestCase):
    """test HealthForm validation data"""

    def test_valid_data(self):
        """test HealthForm with valid data"""
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
        form = HealthForm(self.usertest, -120, data)
        self.assertTrue(form.is_valid())

    def test_required_fields(self):
        """test HealthForm required field"""
        form = HealthForm(self.usertest, -120, {})
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)
        self.assertEqual(form.errors, {
            'date_health': ['Ce champ est obligatoire.'],
            'time_health': ['Ce champ est obligatoire.'],
            'type_alternative_field': ['Ce champ est obligatoire.'],
            '__all__':["Vous n'avez pas renseigné de durée pour cette activité"],
            })


    def test_duration_0(self):
        """test HealthForm invalid cause duration == 0"""
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
        form = HealthForm(self.usertest, -120, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)
        self.assertEqual(form.errors, {
            '__all__':["Vous n'avez pas renseigné de durée pour cette activité"],
            })

    @freeze_time("2020-05-26 23:59:59", tz_offset=+2)
    def test_date_form_gt_today(self):
        """test HealthForm with invalid date"""
        data = {
            'date_health':datetime.date(2020, 5, 27),
            'time_health':datetime.time(3, 56),
            'duration_hour':1,
            'duration_min':30,
            'type_alternative_field':'So',
            'sp_field':self.db_alternative_activity_sp.id,
            'so_field':self.db_alternative_activity_so.id,
            'su_field':self.db_alternative_substitut_p24.id,
        }
        form = HealthForm(self.usertest, -120, data)
        self.assertRaises(ValidationError)
        self.assertEqual(form.errors, {
                '__all__':["Vous ne pouvez pas enregistrer d'action saine pour les jours à venir"],
                })

    @freeze_time("2020-05-26 23:59:59", tz_offset=+2)
    def test_date_form_inf_today(self):
        """test HealthForm with valid date"""
        data = {
            'date_health':datetime.date(2020, 5, 25),
            'time_health':datetime.time(2, 56),
            'duration_hour':1,
            'duration_min':30,
            'type_alternative_field':'So',
            'sp_field':self.db_alternative_activity_sp.id,
            'so_field':self.db_alternative_activity_so.id,
            'su_field':self.db_alternative_substitut_p24.id,
        }
        form = HealthForm(self.usertest, -120, data)
        self.assertTrue(form.is_valid())

class ChooseAlternativeFormWithEmptyFieldsTestCase(HealthFormTestCase):
    """test ChooseAlternativeFormWithEmptyFields"""

    def test_valid_empty_data(self):
        """test ChooseAlternativeFormWithEmptyFields is still valid with empty data"""
        data = {'type_alternative_field':'empty'}
        form = ChooseAlternativeFormWithEmptyFields(self.usertest, data)
        self.assertTrue(form.is_valid())
        data = {
            'type_alternative_field':'empty',
            'sp_field':'empty',
            'so_field':'empty',
            'lo_field':'empty',
            'su_field':'empty',
            }
        form = ChooseAlternativeFormWithEmptyFields(self.usertest, data)
        self.assertTrue(form.is_valid())
