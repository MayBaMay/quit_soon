#!/usr/bin/env python

"""Test pages report and Objectif showing user stats"""

import datetime
from datetime import date as real_date
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from QuitSoonApp.tests import FakeTodayDate
from ..MOCK_DATA import (
    Create_packs, row_paquet_data,
    Create_smoke, row_conso_cig_data,
    )
from QuitSoonApp.models import UserProfile


class ReportViewTestCase1(TestCase):
    """test report view"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'TestUser', 'test@test.com', 'testpassword')
        self.client.login(username=self.user.username, password='testpassword')

    def test_get_report_view_anonymous_user(self):
        """test report view with anonymous user"""
        self.client.logout()
        response = self.client.get(reverse('QuitSoonApp:report'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context, {})

    def test_user_no_profile(self):
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

    @mock.patch('datetime.date', FakeTodayDate)
    def test__user_with_profile(self):
        """test report view using FakeTodayDate as mock for date.today()"""
        self.profile = UserProfile.objects.create(
            user=self.user,
            date_start="2019-09-28",
            starting_nb_cig=20,
        )
        value = datetime.date.today()
        self.assertEqual(value, datetime.date(2019, 11, 28))
        self.assertIsInstance(value, datetime.date)
        self.assertIsInstance(value, FakeTodayDate)
        self.assertIsInstance(datetime.date.today(), FakeTodayDate)
        packs = Create_packs(self.user, row_paquet_data)
        packs.populate_db()
        smokes = Create_smoke(self.user, row_conso_cig_data)
        smokes.populate_db()
        response = self.client.get(reverse('QuitSoonApp:report'))
        self.assertEqual(response.context['total_number'], 329)
        self.assertEqual(response.context['average_number'], 5)
        self.assertEqual(response.context['non_smoked'], 911)
        self.assertEqual(response.context['total_money'], Decimal('157.91'))
        self.assertEqual(response.context['average_money'], Decimal('2.55'))
        self.assertEqual(response.context['saved_money'], Decimal('437.29'))


class objectifsViewTestCase(TestCase):
    pass
