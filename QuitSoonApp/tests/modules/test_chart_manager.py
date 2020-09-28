#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code

"""Test ChartManager module"""

import datetime
from freezegun import freeze_time

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.models import UserProfile
from QuitSoonApp.modules import ChartManager
from ..MOCK_DATA import (
    CreatePacks, CreateSmoke,
    CreateAlternative, CreateConsoAlternative,
    row_alternative_data, row_paquet_data,
    row_conso_cig_data, row_conso_alt_data
    )


class ChartManagerTestCase(TestCase):
    """Test ChartManager class"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        UserProfile.objects.create(
            user=self.usertest,
            date_start=datetime.date(2019, 9, 28),
            starting_nb_cig=20
        )
        self.client.login(
            username=self.usertest.username,
            password='arandompassword'
            )
        self.packs = CreatePacks(self.usertest, row_paquet_data)
        self.packs.populate_db()
        self.smokes = CreateSmoke(self.usertest, row_conso_cig_data)
        self.smokes.populate_db()
        self.alternatives = CreateAlternative(self.usertest, row_alternative_data)
        self.alternatives.populate_db()
        self.healthy = CreateConsoAlternative(self.usertest, row_conso_alt_data)
        self.healthy.populate_db()


    @freeze_time("2019-11-26 20:21:34")
    def test_time_chart_data(self):
        """test time_chart_data method"""
        user_options = {
            'charttype':'time',
             'period':'Jour',
             'dates_range': 0
             }
        chart = ChartManager(self.usertest, user_options, -120)
        self.assertEqual(chart.time_chart_data(), {
            'name': None,
            'index': [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23
                ],
            'data': {
                'base':
                    [0.0,
                     0.0169491525,
                     0.0,
                     0.3898305085,
                     0.3898305085,
                     0.406779661,
                     0.2203389831,
                     0.4237288136,
                     0.2711864407,
                     0.4576271186,
                     0.4576271186,
                     0.6271186441,
                     0.813559322,
                     0.593220339,
                     0.4406779661,
                     0.0,
                     0.0,
                     0.0,
                     0.0,
                     0.0,
                     0.0,
                     0.0,
                     0.0169491525,
                     0.0338983051]
                    },
            'columns': 'Moyenne par heure'
            }
        )

    @freeze_time("2019-11-26 20:21:34")
    def test_generate_graph_data(self):
        """test generate_graph_data method"""
        user_options = {
            'charttype':'nb_cig',
             'period':'Jour',
             'dates_range': 0
             }
        chart = ChartManager(self.usertest, user_options, -120)
        self.assertEqual(chart.generate_graph_data(), {
            'date': [
                datetime.datetime(2019, 9, 28, 0, 0),
                datetime.datetime(2019, 9, 29, 0, 0),
                datetime.datetime(2019, 9, 30, 0, 0),
                datetime.datetime(2019, 10, 1, 0, 0),
                datetime.datetime(2019, 10, 2, 0, 0),
                datetime.datetime(2019, 10, 3, 0, 0),
                datetime.datetime(2019, 10, 4, 0, 0),
                datetime.datetime(2019, 10, 5, 0, 0),
                datetime.datetime(2019, 10, 6, 0, 0),
                datetime.datetime(2019, 10, 7, 0, 0),
                datetime.datetime(2019, 10, 8, 0, 0),
                datetime.datetime(2019, 10, 9, 0, 0),
                datetime.datetime(2019, 10, 10, 0, 0),
                datetime.datetime(2019, 10, 11, 0, 0),
                datetime.datetime(2019, 10, 12, 0, 0),
                datetime.datetime(2019, 10, 13, 0, 0),
                datetime.datetime(2019, 10, 14, 0, 0),
                datetime.datetime(2019, 10, 15, 0, 0),
                datetime.datetime(2019, 10, 16, 0, 0),
                datetime.datetime(2019, 10, 17, 0, 0),
                datetime.datetime(2019, 10, 18, 0, 0),
                datetime.datetime(2019, 10, 19, 0, 0),
                datetime.datetime(2019, 10, 20, 0, 0),
                datetime.datetime(2019, 10, 21, 0, 0),
                datetime.datetime(2019, 10, 22, 0, 0),
                datetime.datetime(2019, 10, 23, 0, 0),
                datetime.datetime(2019, 10, 24, 0, 0),
                datetime.datetime(2019, 10, 25, 0, 0),
                datetime.datetime(2019, 10, 26, 0, 0),
                datetime.datetime(2019, 10, 27, 0, 0),
                datetime.datetime(2019, 10, 28, 0, 0),
                datetime.datetime(2019, 10, 29, 0, 0),
                datetime.datetime(2019, 10, 30, 0, 0),
                datetime.datetime(2019, 10, 31, 0, 0),
                datetime.datetime(2019, 11, 1, 0, 0),
                datetime.datetime(2019, 11, 2, 0, 0),
                datetime.datetime(2019, 11, 3, 0, 0),
                datetime.datetime(2019, 11, 4, 0, 0),
                datetime.datetime(2019, 11, 5, 0, 0),
                datetime.datetime(2019, 11, 6, 0, 0),
                datetime.datetime(2019, 11, 7, 0, 0),
                datetime.datetime(2019, 11, 8, 0, 0),
                datetime.datetime(2019, 11, 9, 0, 0),
                datetime.datetime(2019, 11, 10, 0, 0),
                datetime.datetime(2019, 11, 11, 0, 0),
                datetime.datetime(2019, 11, 12, 0, 0),
                datetime.datetime(2019, 11, 13, 0, 0),
                datetime.datetime(2019, 11, 14, 0, 0),
                datetime.datetime(2019, 11, 15, 0, 0),
                datetime.datetime(2019, 11, 16, 0, 0),
                datetime.datetime(2019, 11, 17, 0, 0),
                datetime.datetime(2019, 11, 18, 0, 0),
                datetime.datetime(2019, 11, 19, 0, 0),
                datetime.datetime(2019, 11, 20, 0, 0),
                datetime.datetime(2019, 11, 21, 0, 0),
                datetime.datetime(2019, 11, 22, 0, 0),
                datetime.datetime(2019, 11, 23, 0, 0),
                datetime.datetime(2019, 11, 24, 0, 0),
                datetime.datetime(2019, 11, 25, 0, 0),
                datetime.datetime(2019, 11, 26, 0, 0)
                ],
            'activity_duration': [
                85, 0, 0, 0, 0, 30, 0, 0, 0, 0, 30, 30, 60, 98, 0, 0, 30, 0,
                30, 0, 0, 155, 0, 0, 30, 0, 50, 0, 30, 60, 0, 55, 30, 90, 0,
                0, 0, 30, 0, 40, 0, 30, 0, 55, 0, 0, 175, 0, 30, 0, 30, 0, 0,
                0, 0, 100, 0, 0, 75, 0
                ],
            'nb_cig': [
                12, 10, 11, 12, 1, 14, 8, 9, 6, 7, 7, 5, 6, 5, 8, 7, 6, 7, 6,
                 4, 10, 9, 5, 4, 6, 5, 7, 5, 6, 3, 4, 6, 2, 4, 6, 5, 3, 4, 2,
                 6, 3, 4, 5, 7, 4, 4, 5, 2, 2, 3, 6, 5, 7, 8, 8, 0, 2, 0, 0, 1
                ]
            }
        )

    @freeze_time("2019-11-26 20:21:34")
    def test_df_period_chart(self):
        """test df_period_chart method"""
        user_options = {
            'charttype':'nb_cig',
             'period':'Mois',
             'dates_range': 0
             }
        chart = ChartManager(self.usertest, user_options, -120)
        test_df = chart.df_period_chart(chart.generate_graph_data())
        self.assertEqual(test_df.loc['09/19', 'nb_cig'], 33)
        self.assertEqual(test_df.loc['10/19', 'nb_cig'], 194)
        self.assertEqual(test_df.loc['11/19', 'nb_cig'], 102)
        self.assertEqual(test_df.loc['09/19', 'activity_duration'], 85)
        self.assertEqual(test_df.loc['10/19', 'activity_duration'], 808)
        self.assertEqual(test_df.loc['11/19', 'activity_duration'], 565)

    @freeze_time("2019-11-26 20:21:34")
    def test_df_period_chart_fail(self):
        """test df_period_chart method"""
        user_options = {
            'charttype':'nb_cig',
             'period':'gqfgqeqfgq',
             'dates_range': 0
             }
        chart = ChartManager(self.usertest, user_options, -120)
        test_df = chart.df_period_chart(chart.generate_graph_data())
        self.assertEqual(test_df.nb_cig.to_list(), [
            12, 10, 11, 12, 1, 14, 8, 9, 6, 7, 7, 5, 6, 5, 8, 7, 6, 7, 6,
             4, 10, 9, 5, 4, 6, 5, 7, 5, 6, 3, 4, 6, 2, 4, 6, 5, 3, 4, 2,
             6, 3, 4, 5, 7, 4, 4, 5, 2, 2, 3, 6, 5, 7, 8, 8, 0, 2, 0, 0, 1
            ])
        self.assertEqual(test_df.activity_duration.to_list(), [
            85, 0, 0, 0, 0, 30, 0, 0, 0, 0, 30, 30, 60, 98, 0, 0, 30, 0,
            30, 0, 0, 155, 0, 0, 30, 0, 50, 0, 30, 60, 0, 55, 30, 90, 0,
            0, 0, 30, 0, 40, 0, 30, 0, 55, 0, 0, 175, 0, 30, 0, 30, 0, 0,
            0, 0, 100, 0, 0, 75, 0
            ])

    @freeze_time("2019-11-26 20:21:34")
    def test_resize_chart(self):
        """test resize_chart method"""
        user_options = {
            'charttype':'nb_cig',
             'period':'Jour',
             'dates_range': -5
             }
        chart = ChartManager(self.usertest, user_options, -120)
        user_dict = chart.generate_graph_data()
        df_chart = chart.resize_chart(chart.df_period_chart(user_dict))
        # 7 nb_cig + 7 activity
        self.assertEqual(df_chart.size, 14)

    @freeze_time("2019-11-26 20:21:34")
    def test_get_parsed_data(self):
        """test get_parsed_data method"""
        user_options = {
            'charttype':'nb_cig',
             'period':'Jour',
             'dates_range': -5
             }
        chart = ChartManager(self.usertest, user_options, -120)
        self.assertEqual(chart.get_parsed_data, {
            'columns': ['nb_cig', 'activity_duration'],
            'index':  [
                '15/11/19',
                '16/11/19',
                '17/11/19',
                '18/11/19',
                '19/11/19',
                '20/11/19',
                '21/11/19'
                ],
            'data': {
                'base': [ 2, 3, 6, 5, 7, 8, 8],
                'activity': [30, 0, 30, 0, 0, 0, 0]
                },
            'min_cig': 20
        })
