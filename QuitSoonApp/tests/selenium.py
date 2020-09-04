# -*- coding: utf-8 -*-

from datetime import datetime
from freezegun import freeze_time

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TransactionTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.firefox.webdriver import WebDriver

from QuitSoonApp.models import UserProfile
from QuitSoonApp.views import (
    today, smoke, smoke_list,
    health, health_list, report,
    get_client_offset,
)

class ClientOffsetTestCase(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        """setup tests"""
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        """teardown tests"""
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            'TestUser', 'test@test.com', 'testpassword')
        self.client.login(username=self.user.username, password='testpassword')
        UserProfile.objects.create(
            user=self.user,
            date_start='2020-05-13',
            starting_nb_cig=20
        )

    @freeze_time("2012-01-14 03:21:34", tz_offset=-4)
    def test_smoke_client_offset(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/smoke/'))
