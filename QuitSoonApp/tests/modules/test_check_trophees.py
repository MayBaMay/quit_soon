#!/usr/bin/env python

"""Module testing health user action manager module"""

import datetime
from datetime import datetime as dt
from datetime import date
import calendar
import pandas as pd
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from QuitSoonApp.modules.check_trophees import Trophee_checking
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Trophee
    )
from QuitSoonApp.modules import SmokeStats

from ..MOCK_DATA import (
    Create_packs, Create_smoke,
    row_paquet_data, fake_smoke
    )

class CheckTropheeTestCase(TestCase):
    """class testing Create_smoke """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'NewUserTest', 'test@test.com', 'testpassword')
        self.profile = UserProfile.objects.create(
            user=self.user,
            date_start="2020-06-19",
            starting_nb_cig=20
            )
        self.packs = Create_packs(self.user, row_paquet_data)
        self.packs.populate_db()
        self.smoke = Create_smoke(self.user, fake_smoke)
        self.smoke.populate_db()
        stats = SmokeStats(self.user, datetime.date(2020, 7, 20))
        self.check_prophee = Trophee_checking(stats)

    def test_values_per_dates(self):
        df = self.check_prophee.values_per_dates
        df.index = pd.to_datetime(df.index)
        self.assertEqual(df.loc['2020-06-19', 'nb_cig'], 19)
        self.assertEqual(df.loc['2020-06-20', 'nb_cig'], 14)
        self.assertEqual(df.shape[0], 2)
