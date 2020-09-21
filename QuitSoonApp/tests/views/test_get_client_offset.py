#!/usr/bin/env python

# """ """

import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from QuitSoonApp.views import (
    get_client_offset,
    update_dt_user_model_field
)
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
)

class TestUpdateDtUserModelField(TestCase):

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'TestUser', 'test@test.com', 'testpassword')
        self.client.login(username='TestUser', password='testpassword')

        db_pack_ind = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        self.conso1 = ConsoCig.objects.create(
            user=self.user,
            datetime_cig=datetime.datetime(2020, 5, 12, 23, 5, tzinfo=pytz.utc),
            paquet=db_pack_ind,
            given=False,
        )
        self.conso2 = ConsoCig.objects.create(
            user=self.user,
            datetime_cig=datetime.datetime(2020, 5, 13, 1, 5, tzinfo=pytz.utc),
            paquet=db_pack_ind,
            given=False,
        )
        alternative_sp = Alternative.objects.create(
            user=self.user,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            )
        alternative_su = Alternative.objects.create(
            user=self.user,
            type_alternative='Su',
            substitut='P',
            nicotine=2,
            )
        self.conso3 = ConsoAlternative.objects.create(
            user=self.user,
            datetime_alter=datetime.datetime(2020, 5, 13, 9, 55, tzinfo=pytz.utc),
            alternative=alternative_sp,
            )
        self.conso4 = ConsoAlternative.objects.create(
            user=self.user,
            datetime_alter=datetime.datetime(2020, 5, 13, 20, 55, tzinfo=pytz.utc),
            alternative=alternative_su,
            )

    def test_get_client_offset(self):
        """test function get_client_offset"""
        session = self.client.session
        session['detected_tz'] = -360
        session.save()
        response = self.client.get(reverse('QuitSoonApp:today'))
        get_client_offset(response.content)

    def test_update_dt_user_model_field(self):
        """test function update_dt_user_model_field"""
        update_dt_user_model_field(self.user, -60)
        conso1 = ConsoCig.objects.get(pk=self.conso1.id)
        self.assertEqual(conso1.user_dt, datetime.datetime(2020, 5, 13, 0, 5, tzinfo=pytz.utc))
        conso2 = ConsoCig.objects.get(pk=self.conso2.id)
        self.assertEqual(conso2.user_dt, datetime.datetime(2020, 5, 13, 2, 5, tzinfo=pytz.utc))
        conso3 = ConsoAlternative.objects.get(pk=self.conso3.id)
        self.assertEqual(conso3.user_dt, datetime.datetime(2020, 5, 13, 10, 55, tzinfo=pytz.utc))
        conso4 = ConsoAlternative.objects.get(pk=self.conso4.id)
        self.assertEqual(conso4.user_dt, datetime.datetime(2020, 5, 13, 21, 55, tzinfo=pytz.utc))
