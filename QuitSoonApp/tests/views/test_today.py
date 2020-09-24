#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=W0611 #False Positiv Unused today imported from QuitSoonApp.views (unused-import)
# pylint: disable=duplicate-code

"""tests views related to user paquets or smoking """


import datetime
import pytz
from freezegun import freeze_time

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from QuitSoonApp.views import today
from QuitSoonApp.models import (
    UserProfile, Paquet, ConsoCig
)

class PacksAndSmokeTestCase(TestCase):
    """
    Tests on parameters page packs and smoking page
    """

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.client.login(username=self.usertest.username, password='arandompassword')
        UserProfile.objects.create(
            user=self.usertest,
            date_start='2020-05-13',
            starting_nb_cig=20
        )
        self.db_pack_ind = Paquet.objects.create(
        user=self.usertest,
        type_cig='IND',
        brand='CAMEL',
        qt_paquet=20,
        price=10,
        )
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 9, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )

    @freeze_time("2020-05-13 20:21:34")
    def test_today_view_1sr_day(self):
        """Test get today view"""
        response = self.client.get(reverse('QuitSoonApp:today'))
        self.assertTemplateUsed(response, 'QuitSoonApp/today.html')
        self.assertEqual(response.context['smoke_today'], 1)
        self.assertEqual(response.context['average_number'], 1)
        self.assertEqual(response.context['lastsmoke'], '11 heures ')

    @freeze_time("2020-05-14 20:21:34")
    def test_today_view_get(self):
        """Test get today view"""
        ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 14, 19, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )
        response = self.client.get(reverse('QuitSoonApp:today'))
        self.assertTemplateUsed(response, 'QuitSoonApp/today.html')
        self.assertEqual(response.context['smoke_today'], 1)
        self.assertEqual(response.context['average_number'], 1)
        self.assertEqual(response.context['lastsmoke'], '1 heure ')
