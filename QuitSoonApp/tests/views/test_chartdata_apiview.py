 #!/usr/bin/env python

"""Test ChartData APIView"""

import datetime
import pytz
from unittest import mock
from unittest.mock import patch
import json

from rest_framework.test import APITestCase, APIRequestFactory
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
from QuitSoonApp.views import ChartData


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
class ChartDataSmokingDataTestCase(APITestCase, BaseTestCase):
    """Test API return all smoking data"""

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.client.login(username=self.usertest.username, password='arandompassword')
        self.packs = Create_packs(self.usertest, row_paquet_data)
        self.packs.populate_db()
        self.smokes = Create_smoke(self.usertest, row_conso_cig_data)
        self.smokes.populate_db()

    def test_1(self, *args):

        factory = APIRequestFactory()
        view = ChartData.as_view()
        request = factory.get('/ChartApi/', {'period': 'Jour', 'show_healthy': False, 'charttype': 'nb_cig', 'datesRange': 0})

        response = self.client.get(reverse('QuitSoonApp:ChartApi'), kwargs=request)
        print(response.content)
