#!/usr/bin/env python

"""tests views related to user paquets or smoking """


from decimal import Decimal
import datetime
import pytz
from freezegun import freeze_time

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from QuitSoonApp.views import today
from QuitSoonApp.models import (
    UserProfile, Paquet, ConsoCig, ConsoAlternative
)


class PacksAndSmokeTestCase(TestCase):
    """
    Tests on parameters page packs and smoking page
    """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'TestUser', 'test@test.com', 'testpassword')
        self.client.login(username=self.user.username, password='testpassword')
        UserProfile.objects.create(
            user=self.user,
            date_start='2020-05-13',
            starting_nb_cig=20
        )
        self.db_pack_ind = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        ConsoCig.objects.create(
            user=self.user,
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
            user=self.user,
            datetime_cig=datetime.datetime(2020, 5, 14, 19, 5, tzinfo=pytz.utc),
            paquet=self.db_pack_ind,
            given=False,
        )
        response = self.client.get(reverse('QuitSoonApp:today'))
        self.assertTemplateUsed(response, 'QuitSoonApp/today.html')
        self.assertEqual(response.context['smoke_today'], 1)
        self.assertEqual(response.context['average_number'], 1)
        self.assertEqual(response.context['lastsmoke'], '1 heure ')
