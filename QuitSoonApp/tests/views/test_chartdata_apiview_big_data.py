#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code
# pylint: disable=W0613 #Unused argument 'args' (unused-argument)


"""Test ChartData APIView with big data several month"""

from unittest import mock
import datetime
import pytz

from django.test import TestCase
from django.utils import timezone

from QuitSoonApp.models import UserProfile
from ..MOCK_DATA import (
    CreatePacks, CreateSmoke,
    CreateAlternative, CreateConsoAlternative,
    row_alternative_data, row_paquet_data,
    row_conso_cig_data, row_conso_alt_data
    )
from .test_chartdata_apiview import BaseChartDataSTestCase


def mocked_now():
    """This is the function that replaces django.utils.timezone.now()"""
    return NOW_FOR_TESTING

def a_func():
    """This function shows that the mocking is in effect even outside of the TestMyTest scope."""
    return timezone.now()


# Make now() a constant
NOW_FOR_TESTING = datetime.datetime(2019, 11, 26, 20, tzinfo=pytz.timezone('utc'))

@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class TestMyTest(TestCase):
    """test mock now"""
    def test_time_zone(self, *args):
        """After patching, mock passes in some extra vars. Put *args to handle them."""
        self.assertEqual(timezone.now(), NOW_FOR_TESTING)
        self.assertEqual(timezone.now().date(), NOW_FOR_TESTING.date())
        self.assertEqual(mocked_now(), NOW_FOR_TESTING)


@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class ChartDataSmokingBigData(BaseChartDataSTestCase):
    """Test API with big data to test month, weeke and resize function"""

    def setUp(self):
        """setup tests"""
        super().setUp()
        UserProfile.objects.create(
            user=self.usertest,
            date_start=datetime.date(2019, 9, 28),
            starting_nb_cig=20
        )
        self.packs = CreatePacks(self.usertest, row_paquet_data)
        self.packs.populate_db()
        self.smokes = CreateSmoke(self.usertest, row_conso_cig_data)
        self.smokes.populate_db()
        self.alternatives = CreateAlternative(self.usertest, row_alternative_data)
        self.alternatives.populate_db()
        self.healthy = CreateConsoAlternative(self.usertest, row_conso_alt_data)
        self.healthy.populate_db()

    def test_chart_nb_cig_week(self, *args):
        """test chart with option nb_cig day"""
        data = {
            'charttype': 'nb_cig',
            'label': 'Cigarettes fumées',
            'period': 'Semaine',
            'show-healthy': 'false',
            'datesRange': '0'
            }
        response = self.client.get(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.data, {
            'columns': ['nb_cig', 'activity_duration'],
            'index': [
                "14/10-20/10",
                "21/10-27/10",
                "28/10-03/11",
                "04/11-10/11",
                "11/11-17/11",
                "18/11-24/11",
                "25/11-01/12"
                ],
            'data': {
                'base': [47, 36, 30, 31, 26, 30, 1],
                'activity': [215, 170, 175, 155, 235, 100, 75]
                },
            'min_cig': 20
            }
        )

    def test_chart_money_smoked_month(self, *args):
        """test chart data with money and month options"""
        data = {
            'charttype': 'money_smoked',
            'label': 'Argent parti en fumée (en€)',
            'period': 'Mois',
            'show-healthy': 'false',
            'datesRange': '0'
            }
        response = self.client.get(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.data, {
            'columns': ['money_smoked', 'activity_duration'],
            'index': ["09/19", "10/19", "11/19"],
            'data': {
                'base': [15.85, 93.86, 49.43],
                'activity': [85, 808, 565]
                },
            'min_cig': 20
            }
        )

    def test_chart_nicotine_day_previous_dates(self, *args):
        """test chart API with nicotine and specific dates range"""
        data = {
            'charttype': 'nicotine',
            'label': 'Nicotine (en mg)',
            'period': 'Jour',
            'show-healthy': 'false',
            'datesRange': '-2'
            }
        response = self.client.get(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertJSONEqual(response.data, {
            'columns': ['nicotine', 'activity_duration'],
            'index': [
                "18/11/19",
                "19/11/19",
                "20/11/19",
                "21/11/19",
                "22/11/19",
                "23/11/19",
                "24/11/19"
                ],
            'data': {
                'base': [0.0, 0.0, 0.0, 0.0, 0.0, 9.0, 0.0],
                'activity': [0, 0, 0, 0, 100, 0, 0]
                },
            'min_cig': 20
            }
        )
