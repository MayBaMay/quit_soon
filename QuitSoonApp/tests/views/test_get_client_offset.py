#!/usr/bin/env python

# """ """

import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.views import (
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
        db_pack_ind = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        ConsoCig.objects.create(
            user=self.user,
            datetime_cig=datetime.datetime(2020, 5, 12, 23, 5, tzinfo=pytz.utc),
            paquet=db_pack_ind,
            given=False,
        )
        ConsoCig.objects.create(
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
        ConsoAlternative.objects.create(
            user=self.user,
            datetime_alter=datetime.datetime(2020, 5, 13, 9, 55, tzinfo=pytz.utc),
            alternative=alternative_sp,
            )
        ConsoAlternative.objects.create(
            user=self.user,
            datetime_alter=datetime.datetime(2020, 5, 13, 20, 55, tzinfo=pytz.utc),
            alternative=alternative_su,
            )

    def test_view(self):
        update_dt_user_model_field(self.user, -60)
        conso = ConsoCig.objects.filter(user=self.user)
        self.assertEqual(conso[0].user_dt, datetime.datetime(2020, 5, 13, 0, 5, tzinfo=pytz.utc))
        self.assertEqual(conso[1].user_dt, datetime.datetime(2020, 5, 13, 2, 5, tzinfo=pytz.utc))
        conso = ConsoAlternative.objects.filter(user=self.user)
        self.assertEqual(conso[0].user_dt, datetime.datetime(2020, 5, 13, 10, 55, tzinfo=pytz.utc))
        self.assertEqual(conso[1].user_dt, datetime.datetime(2020, 5, 13, 21, 55, tzinfo=pytz.utc))
