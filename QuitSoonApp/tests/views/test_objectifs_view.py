#!/usr/bin/env python
# pylint: disable=W0613 #Unused argument 'args' (unused-argument)
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code


"""Module testing objectifs view """

from unittest import mock
import datetime
import pytz

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from QuitSoonApp.models import UserProfile
from ..MOCK_DATA import (
    CreatePacks, CreateSmoke,
    row_paquet_data, fake_smoke_for_trophies,
    )


def mocked_now():
    """This is the function that replaces django.utils.timezone.now()"""
    return NOW_FOR_TESTING

def a_func():
    """This function shows that the mocking is in effect even outside of the TestMyTest scope."""
    return timezone.now()

# Make now() a constant
NOW_FOR_TESTING = datetime.datetime(2020, 12, 31, 12, tzinfo=pytz.timezone('utc'))

@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class TestMyTest(TestCase):
    """test mock now """
    def test_time_zone(self, *args):
        """test mock now """
        # After patching, mock passes in some extra vars. Put *args to handle them.
        self.assertEqual(timezone.now(), NOW_FOR_TESTING)
        self.assertEqual(timezone.now().date(), NOW_FOR_TESTING.date())
        self.assertEqual(mocked_now(), NOW_FOR_TESTING)


@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class ReportViewTestCase(TestCase):
    """test report view"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.packs = CreatePacks(self.usertest, row_paquet_data)
        self.packs.populate_db()
        self.smokes = CreateSmoke(self.usertest, fake_smoke_for_trophies)
        self.smokes.populate_db()

    def test_get_report_view_anonymous_user(self, *args):
        """test report view with anonymous user"""
        self.client.logout()
        response = self.client.get(reverse('QuitSoonApp:objectifs'))
        self.assertEqual(response.status_code, 302, *args)
        self.assertRedirects(
            response,
             '/login/',
             status_code=302,
             target_status_code=200,
             fetch_redirect_response=True
             )

    def test_user_no_profile(self, *args):
        """test report view without a user profile"""
        self.client.login(username=self.usertest.username, password='arandompassword')
        response = self.client.get(reverse('QuitSoonApp:objectifs'))
        self.assertEqual(response.status_code, 302, *args)
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
        self.client.login(username=self.usertest.username, password='arandompassword')
        UserProfile.objects.create(
            user=self.usertest,
            date_start="2020-06-19",
            starting_nb_cig=20,
        )
        response = self.client.get(reverse('QuitSoonApp:objectifs'))
        self.assertEqual(
            response.context['challenges'],
            {(15, 3): True, (15, 7): True, (10, 3): True, (10, 7): True,
            (5, 3): True, (5, 7): True, (4, 3): True, (4, 7): True,
            (3, 3): True, (3, 7): True, (2, 3): True, (2, 7): True, (1, 3): True,
            (1, 7): True, (0, 1): True, (0, 2): True, (0, 3): True, (0, 4): True,
            (0, 7): True, (0, 10): True, (0, 15): True, (0, 20): True,
            (0, 25): True, (0, 30): True, (0, 60): True, (0, 90): False,
            (0, 120): False, (0, 150): False, (0, 180): False, (0, 210): False,
            (0, 240): False, (0, 270): False, (0, 300): False, (0, 330): False}
            )
