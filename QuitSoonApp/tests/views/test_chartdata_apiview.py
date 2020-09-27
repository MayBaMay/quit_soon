#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code
# pylint: disable=W0613 #Unused argument 'args' (unused-argument)



"""Test ChartData APIView"""

from unittest import mock
import datetime
import pytz

from rest_framework.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from QuitSoonApp.models import UserProfile, Paquet, ConsoCig
from ..MOCK_DATA import (
    CreatePacks, CreateSmoke,
    CreateAlternative, CreateConsoAlternative,
    row_alternative_data, row_paquet_data,
    fake_smoke, fake_healthy,
    )


def mocked_now():
    """This is the function that replaces django.utils.timezone.now()"""
    return NOW_FOR_TESTING

def a_func():
    """This function shows that the mocking is in effect even outside of the TestMyTest scope."""
    return timezone.now()

# Make now() a constant
NOW_FOR_TESTING = datetime.datetime(2020, 6, 21, 20, tzinfo=pytz.timezone('utc'))

@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class TestMyTest(TestCase):
    """test mock now"""
    def test_time_zone(self, *args):
        """After patching, mock passes in some extra vars. Put *args to handle them."""
        self.assertEqual(timezone.now(), NOW_FOR_TESTING)
        self.assertEqual(timezone.now().date(), NOW_FOR_TESTING.date())
        self.assertEqual(mocked_now(), NOW_FOR_TESTING)


@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class BaseChartDataSTestCase(APITestCase):
    """Test API return all smoking data first day using app"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.client.login(
            username=self.usertest.username,
            password='arandompassword'
            )
        db_pack_ind = Paquet.objects.create(
            user=self.usertest,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            price_per_cig=0.5,
        )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 21, 10, 15, tzinfo=pytz.utc),
            paquet=None,
            given=True,
            )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 6, 21, 13, 15, tzinfo=pytz.utc),
            paquet=db_pack_ind,
            )
        self.url = reverse('QuitSoonApp:ChartApi')


@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class ChartDataSmokingDataFirstDayTestCase(BaseChartDataSTestCase):
    """Test API return all smoking data first day using app"""

    def setUp(self):
        """setup tests"""
        super().setUp()
        UserProfile.objects.create(
            user=self.usertest,
            date_start=datetime.date(2020, 6, 21),
            starting_nb_cig=15
        )

    def test_time_chart_data(self, *args):
        """Test time chart data first day app"""
        url = reverse('QuitSoonApp:ChartApi')
        data = {
            'charttype': 'time',
            'label': 'Consommation moyenne de cigarettes par heure',
            'period': 'Jour',
            'show-healthy': 'false',
            'datesRange': '0'
            }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.data, {
            'name': None,
            'index': [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23
                ],
            'data':
                {'base': [
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                    0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
                    ]
                 },
                'columns': 'Moyenne par heure'
                }
        )

    def test_generate_graph_data(self, *args):
        """test generate_graph_data data method"""
        data = {
            'charttype': 'nb_cig',
            'label': 'Cigarettes fumées',
            'period': 'Jour',
            'show-healthy': 'false',
            'datesRange': '0'
            }
        response = self.client.get(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.data, {
            'columns': ['nb_cig', 'activity_duration'],
            'index': ['21/06/20'],
            'data': {
                'base': [2],
                'activity': [0]
                },
            'min_cig': 15
            }
        )


@mock.patch('django.utils.timezone.now', side_effect=mocked_now)
class ChartDataSmokingDataThirdDayTestCase(BaseChartDataSTestCase):
    """Test API return all smoking data of the 2 last full days"""

    def setUp(self):
        """setup tests"""
        super().setUp()
        UserProfile.objects.create(
            user=self.usertest,
            date_start=datetime.date(2020, 6, 19),
            starting_nb_cig=15
        )
        self.packs = CreatePacks(self.usertest, row_paquet_data)
        self.packs.populate_db()
        self.smokes = CreateSmoke(self.usertest, fake_smoke)
        self.smokes.populate_db()
        self.alternatives = CreateAlternative(self.usertest, row_alternative_data)
        self.alternatives.populate_db()
        self.healthy = CreateConsoAlternative(self.usertest, fake_healthy)
        self.healthy.populate_db()

    def test_time_chart_data(self, *args):
        """test time_chart_data method"""

        data = {
            'charttype': 'time',
            'label': 'Consommation moyenne de cigarettes par heure',
            'period': 'Jour',
            'show-healthy': 'false',
            'datesRange': '0'
            }
        response = self.client.get(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.data, {
            'name': None,
            'index': [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23
                ],
            'data':
                {'base': [
                    0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 1.5, 1.5,
                    1.0, 1.5, 1.0, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.0, 0.5, 0.5
                    ]
                 },
                'columns': 'Moyenne par heure'
                }
        )

    def test_chart_nb_cig_day(self, *args):
        """test chart with option nb_cig day"""
        data = {
            'charttype': 'nb_cig',
            'label': 'Cigarettes fumées',
            'period': 'Jour',
            'show-healthy': 'false',
            'datesRange': '0'
            }
        response = self.client.get(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.data, {
            'columns': ['nb_cig', 'activity_duration'],
            'index': ['19/06/20', '20/06/20', '21/06/20'],
            'data': {
                'base': [19, 14, 2],
                'activity': [70, 95, 0]
                },
            'min_cig': 15
            }
        )

    def test_chart_money_smoked_day(self, *args):
        """test chart Api return data for money"""
        data = {
            'charttype': 'money_smoked',
            'label': 'Argent parti en fumée (en€)',
            'period': 'Jour',
            'show-healthy': 'false',
            'datesRange': '0'
            }
        response = self.client.get(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.data, {
            'columns': ['money_smoked', 'activity_duration'],
            'index': ['19/06/20', '20/06/20', '21/06/20'],
            'data': {
                'base': [9.22, 6.79, 0.5],
                'activity': [70, 95, 0]
                },
            'min_cig': 15
            }
        )

    def test_chart_nicotine_day(self, *args):
        """test chart Api return data for nicotine"""
        data = {
            'charttype': 'nicotine',
            'label': 'Nicotine (en mg)',
            'period': 'Jour',
            'show-healthy': 'false',
            'datesRange': '0'
            }
        response = self.client.get(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.data, {
            'columns': ['nicotine', 'activity_duration'],
            'index': ['19/06/20', '20/06/20', '21/06/20'],
            'data': {
                'base': [13, 19, 0],
                'activity': [70, 95, 0]
                },
            'min_cig': 15
            }
        )
