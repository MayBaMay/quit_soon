#!/usr/bin/env python

"""Module testing report view """

import datetime
import pytz
from decimal import Decimal
from unittest import mock
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from ..MOCK_DATA import (
    BaseTestCase,
    Create_packs, Create_smoke,
    CreateAlternative, CreateConsoAlternative,
    row_paquet_data, row_conso_cig_data,
    row_alternative_data, row_conso_alt_data, fake_smoke
    )
from QuitSoonApp.models import UserProfile

# This is the function that replaces django.utils.timezone.now()
def mocked_now():
    return NOW_FOR_TESTING

# This function shows that the mocking is in effect even outside of the TestMyTest scope.
def a_func():
    return timezone.now()

# Make now() a constant
NOW_FOR_TESTING = datetime.datetime(2019, 11, 27, 20, tzinfo=pytz.timezone('utc'))

@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class TestMyTest(TestCase):
    def test_time_zone(self, *args):
        # After patching, mock passes in some extra vars. Put *args to handle them.
        self.assertEqual(timezone.now(), NOW_FOR_TESTING)
        self.assertEqual(timezone.now().date(), NOW_FOR_TESTING.date())
        self.assertEqual(mocked_now(), NOW_FOR_TESTING)

@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class ReportViewTestCase(BaseTestCase):
    """test report view"""

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.client.login(username=self.usertest.username, password='arandompassword')
        self.packs = Create_packs(self.usertest, row_paquet_data)
        self.packs.populate_db()
        self.smokes = Create_smoke(self.usertest, row_conso_cig_data)
        self.smokes.populate_db()
        self.alternatives = CreateAlternative(self.usertest, row_alternative_data)
        self.alternatives.populate_db()
        self.healthy = CreateConsoAlternative(self.usertest, row_conso_alt_data)
        self.healthy.populate_db()

    def test_get_report_view_anonymous_user(self, *args):
        """test report view with anonymous user"""
        self.client.logout()
        response = self.client.get(reverse('QuitSoonApp:report'))
        self.assertEqual(response.status_code, 302, *args)

    def test_user_no_profile(self, *args):
        """test report view without a user profile"""
        response = self.client.get(reverse('QuitSoonApp:report'))
        self.assertRedirects(
            response,
            '/profile/',
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True
            )

    def test_user_with_profile_smoke_report(self, *args):
        """test smoke reporting in report view"""
        self.profile = UserProfile.objects.create(
            user=self.usertest,
            date_start="2019-09-28",
            starting_nb_cig=20,
        )

        response = self.client.get(reverse('QuitSoonApp:report'))
        self.assertEqual(response.context['smoky_report']['total_number'], 329)
        self.assertEqual(response.context['smoky_report']['average_number'], 5)
        self.assertEqual(response.context['smoky_report']['non_smoked'], 871)
        self.assertEqual(response.context['smoky_report']['total_money'], Decimal('159.16'))
        self.assertEqual(response.context['smoky_report']['average_money'], Decimal('2.65'))
        self.assertEqual(response.context['smoky_report']['saved_money'], Decimal('422.84'))

    def test_user_with_profile_health_report(self, *args):
        """test health reporting in report view"""
        self.profile = UserProfile.objects.create(
            user=self.usertest,
            date_start="2019-09-28",
            starting_nb_cig=20,
        )
        response = self.client.get(reverse('QuitSoonApp:report'))
        self.assertEqual(
            response.context['healthy_report']['activity_stats']['Sp'],
            {'exists': True, 'name': 'Sport', 'day': None, 'week': '1h15', 'month': '4h20'}
            )
        self.assertEqual(
            response.context['healthy_report']['activity_stats']['Lo'],
            {'exists': True, 'name': 'Loisir', 'day': '1h05', 'week': '1h05', 'month': '4h40'}
            )
        self.assertEqual(
            response.context['healthy_report']['substitut_stats']['PAST'],
            {'exists': True, 'name': 'Pastilles', 'day': 1, 'week': 1, 'month': 5}
            )
        self.assertEqual(
            response.context['healthy_report']['substitut_stats']['GM'],
            {'name': 'Gommes à mâcher', 'day': None, 'week': None, 'month': None}
            )

class ReportViewNoDataTestCase(BaseTestCase):
    """test report view"""

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.client.login(username=self.usertest.username, password='arandompassword')
        self.profile = UserProfile.objects.create(
            user=self.usertest,
            date_start="2019-09-28",
            starting_nb_cig=20,
        )

    def test_report_view_no_data(self):
        response = self.client.get(reverse('QuitSoonApp:report'))
        self.assertEqual(response.context['no_data'], True)
