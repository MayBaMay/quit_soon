#!/usr/bin/env python

"""Test pages report and Objectif showing user stats"""

import datetime
from datetime import date as real_date
import pytz
from decimal import Decimal
from unittest import mock
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ..MOCK_DATA import (
    Create_packs, row_paquet_data,
    Create_smoke, row_conso_cig_data,
    )
from QuitSoonApp.models import UserProfile
from django.utils import timezone


# Make now() a constant
NOW_FOR_TESTING = datetime.datetime(2019, 11, 28, 10, tzinfo=pytz.timezone('utc'))

# This is the function that replaces django.utils.timezone.now()
def mocked_now():
    return NOW_FOR_TESTING

# This function shows that the mocking is in effect even outside of the TestMyTest scope.
def a_func():
    return timezone.now()

@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class TestMyTest(TestCase):
    def test_time_zone(self, *args):
        # After patching, mock passes in some extra vars. Put *args to handle them.
        self.assertEqual(timezone.now(), NOW_FOR_TESTING)
        self.assertEqual(timezone.now().date(), NOW_FOR_TESTING.date())
        self.assertEqual(mocked_now(), NOW_FOR_TESTING)

@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class ReportViewTestCase1(TestCase):
    """test report view"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'TestUser', 'test@test.com', 'testpassword')
        self.client.login(username=self.user.username, password='testpassword')

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

    def test_user_with_profile(self, *args):
        """test report view using FakeTodayDate as mock for date.today()"""
        self.profile = UserProfile.objects.create(
            user=self.user,
            date_start="2019-09-28",
            starting_nb_cig=20,
        )
        packs = Create_packs(self.user, row_paquet_data)
        packs.populate_db()
        smokes = Create_smoke(self.user, row_conso_cig_data)
        smokes.populate_db()
        response = self.client.get(reverse('QuitSoonApp:report'))
        self.assertEqual(response.context['total_number'], 329)
        self.assertEqual(response.context['average_number'], 5)
        self.assertEqual(response.context['non_smoked'], 891)
        self.assertEqual(response.context['total_money'], Decimal('159.16'))
        self.assertEqual(response.context['average_money'], Decimal('2.61'))
        self.assertEqual(response.context['saved_money'], Decimal('432.54'))
#     #
# #
# # class objectifsViewTestCase(TestCase):
#     # pass
