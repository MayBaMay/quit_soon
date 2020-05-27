#!/usr/bin/env python

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.forms import (
    TypeAlternativeForm,
    ActivityForm,
    SubstitutForm
    )
from QuitSoonApp.models import Alternative


class test_TypeAlternativeForm(TestCase):
    """test TypeAlternativeForm"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")

    def test_form(self):
        """test ParametersForm"""
        data = {'user':self.user, 'type_alternative':'Ac'}
        form = TypeAlternativeForm(self.user, data=data)
        self.assertTrue(form.is_valid())


class test_ActivityForm(TestCase):
    """test ActivityForm"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")

    def test_form(self):
        """test ActivityForm"""
        data = {'user':self.user, 'type_activity':'Sp', 'activity':'Course à pied'}
        form = ActivityForm(self.user, data=data)
        self.assertTrue(form.is_valid())

class test_SubstitutForm(TestCase):
    """test SubstitutForm"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")

    def test_form(self):
        """test SubstitutForm"""
        data = {'user':self.user, 'substitut':'PAST', 'nicotine':2.0}
        form = SubstitutForm(self.user, data=data)
        self.assertTrue(form.is_valid())
