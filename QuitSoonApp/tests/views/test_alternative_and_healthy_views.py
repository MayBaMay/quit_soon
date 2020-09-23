#!/usr/bin/env python

"""tests views related to user alternatives or healthy actions """

import datetime
import pytz

from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User

from QuitSoonApp.views import (
    alternatives, health,
)
from QuitSoonApp.models import (
    UserProfile, Alternative, ConsoAlternative,
)
from ..MOCK_DATA import BaseTestCase


class AlternativeAndHealthyTestCase(BaseTestCase):
    """
    Tests on parameters pages, health (alternatives) or smoke (packs)
    """

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.client.login(username=self.usertest.username, password='arandompassword')
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2020-05-13',
            starting_nb_cig=20
        )

    def test_alternatives_view_post_succes_alt(self):
        """Test client post a form with alternatives with success"""
        data = {'type_alternative':'Ac',
                'type_activity':'Sp',
                'activity':'Course à pied'}
        response = self.client.post(reverse('QuitSoonApp:alternatives'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/alternatives.html')
        db_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE À PIED',
            )
        self.assertTrue(db_alternative.exists())

    def test_alternatives_view_post_succes_subs(self):
        """Test client post a form with alternatives with success"""
        data = {'type_alternative':'Su',
                'substitut':'P',
                'nicotine':'2',
                }
        response = self.client.post(reverse('QuitSoonApp:alternatives'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/alternatives.html')
        db_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='P',
            nicotine='2',
            )
        self.assertTrue(db_alternative.exists())

    def test_alternatives_view_post_fails_unique(self):
        """Test client post a form with alternatives fails because of IntegrityError"""
        Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='GS',
            nicotine='2',
            )
        data = {'type_alternative':'Su',
                'substitut':'GS',
                'nicotine':'2',
                }
        response = self.client.post(reverse('QuitSoonApp:alternatives'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/alternatives.html')
        db_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='GS',
            nicotine='2',
            )
        self.assertTrue(db_alternative.count(), 1)

    def test_alternatives_view_post_get_only_relevant_form(self):
        """Test client post a form with alternatives with success"""
        data = {'type_alternative':'Su',
                'type_activity':'P',
                'activity':'Course',
                'substitut':'P',
                'nicotine':'2',
                }
        response = self.client.post(reverse('QuitSoonApp:alternatives'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/alternatives.html')
        db_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='P',
            nicotine='2',
            )
        self.assertTrue(db_alternative.exists())

    def test_delete_alternative_views_activity(self):
        """Test client post delete_alternative view with activity data"""
        db_alternative = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='tabacologue',
            )
        response = self.client.post(reverse('QuitSoonApp:delete_alternative', args=[db_alternative.id]))
        self.assertEqual(response.status_code, 302)
        filter_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='tabacologue',
            )
        self.assertFalse(filter_alternative.exists())

    def test_delete_alternative_views_substitut(self):
        """Test client post delete_alternative view with substitut data"""
        db_alternative = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='GM',
            nicotine=None,
            )
        response = self.client.post(reverse('QuitSoonApp:delete_alternative', args=[db_alternative.id]))
        self.assertEqual(response.status_code, 302)
        filter_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            type_activity='GM',
            activity=None,
            )
        self.assertFalse(filter_alternative.exists())

    def test_delete_alternative_views_substitut_used_in_ConsoAlternative(self):
        """Test client post delete_alternative view with substitut data while used in ConsoAlternative"""
        db_alternative = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='GM',
            nicotine=None,
            )
        conso = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 13, 55, tzinfo=pytz.utc),
            alternative=db_alternative,
        )
        filter_conso = ConsoAlternative.objects.filter(
            user=self.usertest,
            alternative=db_alternative,
            )
        self.assertTrue(filter_conso.exists())
        response = self.client.post(reverse('QuitSoonApp:delete_alternative', args=[db_alternative.id]))
        self.assertEqual(response.status_code, 302)
        filter_alternative = Alternative.objects.filter(
            user=self.usertest,
            type_alternative='Su',
            substitut='GM',
            nicotine=None,
            )
        self.assertTrue(filter_alternative.exists())
        self.assertEqual(filter_alternative[0].display, False)

    def test_delete_alternative_views_wrong_arg(self):
        response = self.client.post(reverse(
            'QuitSoonApp:delete_alternative',
            args=[3453]))
        self.assertEqual(response.status_code, 404)

class HealthTestCase(TransactionTestCase):

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            'Newuser', 'test@test.com', 'testpassword')
        self.client.login(username=self.usertest.username, password='testpassword')
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2020-05-13',
            starting_nb_cig=20
        )

        self.alternative_sp = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            )
        self.alternative_so = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='TABACOLOGUE',
            )
        self.alternative_su = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='P',
            nicotine=2,
            )
        self.data_sp = {
            'date_health': datetime.date(2020, 5, 17),
            'time_health': datetime.time(13, 15),
            'type_alternative_field':'Sp',
            'sp_field': self.alternative_sp.id,
            'so_field': self.alternative_so.id,
            'su_field':self.alternative_su.id,
            }
        self.data_su = {
            'date_health': datetime.date(2020, 5, 17),
            'time_health': datetime.time(14, 15),
            'type_alternative_field':'Su',
            'sp_field': self.alternative_sp.id,
            'so_field': self.alternative_so.id,
            'su_field':self.alternative_su.id,
            }
        self.health_sp = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 17, 13, 15, tzinfo=pytz.utc),
            alternative=self.alternative_sp,
            activity_duration=90,
        )
        self.data_id = {'id_health': self.health_sp.id}

    def test_health_get_no_pack(self):
        """ test get health view with no alternative saved by user """
        Alternative.objects.filter(user=self.usertest).all().delete()
        response = self.client.get(reverse('QuitSoonApp:health'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['alternatives'].exists())
        self.assertFalse(response.context['health'].exists())

    def test_health_get_form(self):
        """ test get health view with alternatives saved by user, get form"""
        response = self.client.get(reverse('QuitSoonApp:health'))
        self.assertTrue(response.context['alternatives'].exists())
        self.assertTrue(response.context['health'].exists())
        self.assertTrue('form' in response.context)

    def test_health_post_form_success(self):
        """ test get health view post form"""
        response = self.client.post(reverse('QuitSoonApp:health'), data=self.data_su)
        filter = ConsoAlternative.objects.filter(user=self.usertest, alternative=self.alternative_su)
        self.assertTrue(filter.exists())

    def test_healt_fail_no_duration_activity(self):
        """ test get health view post with error in data : no duration for activity"""
        response = self.client.post(reverse('QuitSoonApp:health'), data=self.data_sp)
        filter = ConsoAlternative.objects.filter(
            user=self.usertest,
            alternative=self.alternative_sp,
            datetime_alter__date=datetime.date(2020, 5, 10)
            )
        self.assertFalse(filter.exists())

    def test_delete_health_fail(self):
        """ test get delete_health view with unexisting ConsoAlternative """
        response = self.client.post(reverse(
            'QuitSoonApp:delete_health',
            args=[40]))
        self.assertEqual(response.status_code, 404)

    def test_delete_health(self):
        """ test get delete_health"""
        response = self.client.post(reverse(
            'QuitSoonApp:delete_health',
            args=[self.health_sp.id]))
        self.assertEqual(response.status_code, 302)
        filter_conso = ConsoAlternative.objects.filter(user=self.usertest, id=self.health_sp.id)
        self.assertFalse(filter_conso.exists())

class HealthListTestCase(BaseTestCase):

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.client.login(username=self.usertest.username, password='arandompassword')

        UserProfile.objects.create(
            user=self.usertest,
            date_start='2020-05-13',
            starting_nb_cig=20
        )
        self.alternative_sp = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            )
        self.alternative_sp2 = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='MARCHE',
            )
        self.alternative_so = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='So',
            activity='TABACOLOGUE',
            )
        self.alternative_su = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='P',
            nicotine=2,
            )
        self.alternative_lo2 = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Lo',
            activity='DESSIN',
            )
        self.conso_1 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 9, 55, tzinfo=pytz.utc),
            alternative=self.alternative_sp,
        )
        self.conso_2 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 13, 55, tzinfo=pytz.utc),
            alternative=self.alternative_so,
        )
        self.conso_3 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 20, 55, tzinfo=pytz.utc),
            alternative=self.alternative_su,
        )
        self.conso_4 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 15, 13, 55, tzinfo=pytz.utc),
            alternative=self.alternative_sp,
        )
        self.conso_5 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 17, 13, 55, tzinfo=pytz.utc),
            alternative=self.alternative_so,
        )
        self.conso_6 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 17, 10, 55, tzinfo=pytz.utc),
            alternative=self.alternative_sp2,
        )
        self.conso_7 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 17, 10, 55, tzinfo=pytz.utc),
            alternative=self.alternative_lo2,
        )

    def test_health_list_get_anonymoususer(self):
        self.client.logout()
        response = self.client.get(reverse('QuitSoonApp:health_list'))
        self.assertEqual(response.status_code, 302)

    def test_health_list_no_alternative_saved(self):
        Alternative.objects.filter(user=self.usertest).delete()
        response = self.client.get(reverse('QuitSoonApp:health_list'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['alternatives'])
        self.assertTrue('health_form' not in response.context.keys())
        self.assertTrue('health' not in response.context.keys())

    def test_health_list_no_health_saved(self):
        ConsoAlternative.objects.filter(user=self.usertest).delete()
        response = self.client.get(reverse('QuitSoonApp:health_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['alternatives'],
                        Alternative.objects.filter(user=self.usertest, display=True))
        self.assertTrue('health_form' not in response.context.keys())
        self.assertTrue('health' not in response.context.keys())

    def test_health_list_empty_fields(self):
        data = {'type_alternative_field':'empty',
                'sp_field':'empty',
                'so_field':'empty',
                'lo_field':'empty',
                'su_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:health_list'),
                                    data=data)
        self.assertTrue(response.context['alternatives'],
                        Alternative.objects.filter(user=self.usertest, display=True))
        self.assertTrue(response.context['health'][0], self.conso_7)
        self.assertTrue(self.conso_6 in response.context['health'])
        self.assertTrue(self.conso_5 in response.context['health'])
        self.assertTrue(self.conso_4 in response.context['health'])
        self.assertTrue(self.conso_3 in response.context['health'])
        self.assertTrue(self.conso_2 in response.context['health'])
        self.assertTrue(self.conso_1 in response.context['health'])
        self.assertEqual(len(response.context['health']), 7)
        self.assertTrue('health_form' in response.context.keys())

    def test_only_type_alternative_field_su(self):
        data = {'type_alternative_field':'Su',
                'sp_field':'empty',
                'so_field':'empty',
                'lo_field':'empty',
                'su_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:health_list'),
                                    data=data)
        self.assertTrue(response.context['health'][0], self.conso_3)
        self.assertEqual(len(response.context['health']), 1)
        self.assertTrue('health_form' in response.context.keys())

    def test_only_type_alternative_field_sp(self):
        data = {'type_alternative_field':'Sp',
                'sp_field':'empty',
                'so_field':'empty',
                'lo_field':'empty',
                'su_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:health_list'),
                                    data=data)
        self.assertFalse(self.conso_7 in response.context['health'])
        self.assertTrue(response.context['health'][0], self.conso_6)
        self.assertFalse(self.conso_5 in response.context['health'])
        self.assertTrue(self.conso_4 in response.context['health'])
        self.assertFalse(self.conso_3 in response.context['health'])
        self.assertFalse(self.conso_2 in response.context['health'])
        self.assertTrue(self.conso_1 in response.context['health'])
        self.assertEqual(len(response.context['health']), 3)
        self.assertTrue('health_form' in response.context.keys())

    def test_only_sp_field(self):
        data = {'type_alternative_field':'Sp',
                'sp_field':self.alternative_sp.id,
                'so_field':'empty',
                'lo_field':'empty',
                'su_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:health_list'),
                                    data=data)
        self.assertFalse(self.conso_7 in response.context['health'])
        self.assertFalse(self.conso_6 in response.context['health'])
        self.assertFalse(self.conso_5 in response.context['health'])
        self.assertTrue(response.context['health'][0], self.conso_4)
        self.assertFalse(self.conso_3 in response.context['health'])
        self.assertFalse(self.conso_2 in response.context['health'])
        self.assertTrue(self.conso_1 in response.context['health'])
        self.assertEqual(len(response.context['health']), 2)
        self.assertTrue('health_form' in response.context.keys())

    def test_only_so_field(self):
        data = {'type_alternative_field':'So',
                'sp_field':'empty',
                'so_field':self.alternative_so.id,
                'lo_field':'empty',
                'su_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:health_list'),
                                    data=data)
        self.assertFalse(self.conso_7 in response.context['health'])
        self.assertFalse(self.conso_6 in response.context['health'])
        self.assertTrue(response.context['health'][0], self.conso_5)
        self.assertFalse(self.conso_4 in response.context['health'])
        self.assertFalse(self.conso_3 in response.context['health'])
        self.assertTrue(self.conso_2 in response.context['health'])
        self.assertFalse(self.conso_1 in response.context['health'])
        self.assertEqual(len(response.context['health']), 2)
        self.assertTrue('health_form' in response.context.keys())

    def test_only_lo_field(self):
        data = {'type_alternative_field':'Lo',
                'sp_field':'empty',
                'so_field':'empty',
                'lo_field':self.alternative_lo2.id,
                'su_field':'empty'}
        response = self.client.post(reverse('QuitSoonApp:health_list'),
                                    data=data)
        self.assertTrue(response.context['health'][0], self.conso_7)
        self.assertEqual(len(response.context['health']), 1)
        self.assertTrue('health_form' in response.context.keys())

    def test_only_su_field(self):
        data = {'type_alternative_field':'Su',
                'sp_field':'empty',
                'so_field':'empty',
                'lo_field':'empty',
                'su_field':self.alternative_su.id}
        response = self.client.post(reverse('QuitSoonApp:health_list'),
                                    data=data)
        self.assertTrue(response.context['health'][0], self.conso_3)
        self.assertEqual(len(response.context['health']), 1)
        self.assertTrue('health_form' in response.context.keys())
