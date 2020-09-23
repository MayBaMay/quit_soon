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
from ..MOCK_DATA import BaseTestCase

class TestUpdateDtUserModelField(BaseTestCase):

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.client.login(username='arandomname', password='arandompassword')

        db_pack_ind = self.camel
        self.conso1 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 12, 23, 5, tzinfo=pytz.utc),
            paquet=db_pack_ind,
            given=False,
        )
        self.conso2 = ConsoCig.objects.create(
            user=self.usertest,
            datetime_cig=datetime.datetime(2020, 5, 13, 1, 5, tzinfo=pytz.utc),
            paquet=db_pack_ind,
            given=False,
        )
        alternative_sp = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE',
            )
        alternative_su = Alternative.objects.create(
            user=self.usertest,
            type_alternative='Su',
            substitut='P',
            nicotine=2,
            )
        self.conso3 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 9, 55, tzinfo=pytz.utc),
            alternative=alternative_sp,
            )
        self.conso4 = ConsoAlternative.objects.create(
            user=self.usertest,
            datetime_alter=datetime.datetime(2020, 5, 13, 20, 55, tzinfo=pytz.utc),
            alternative=alternative_su,
            )

    def test_update_dt_user_model_field(self):
        """test function update_dt_user_model_field"""
        update_dt_user_model_field(self.usertest, -60)
        conso1 = ConsoCig.objects.get(pk=self.conso1.id)
        self.assertEqual(conso1.user_dt, datetime.datetime(2020, 5, 13, 0, 5, tzinfo=pytz.utc))
        conso2 = ConsoCig.objects.get(pk=self.conso2.id)
        self.assertEqual(conso2.user_dt, datetime.datetime(2020, 5, 13, 2, 5, tzinfo=pytz.utc))
        conso3 = ConsoAlternative.objects.get(pk=self.conso3.id)
        self.assertEqual(conso3.user_dt, datetime.datetime(2020, 5, 13, 10, 55, tzinfo=pytz.utc))
        conso4 = ConsoAlternative.objects.get(pk=self.conso4.id)
        self.assertEqual(conso4.user_dt, datetime.datetime(2020, 5, 13, 21, 55, tzinfo=pytz.utc))
