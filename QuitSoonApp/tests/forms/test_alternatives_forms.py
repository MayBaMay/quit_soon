#!/usr/bin/env python
# pylint: disable=C0103 #Method name "test_smokeForm_is_valid" doesn't conform to snake_case naming style (invalid-name)
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code

"""test Forms related to Alternative model"""

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.forms import (
    TypeAlternativeForm,
    ActivityForm,
    SubstitutForm
    )


class test_typealternativeForm(TestCase):
    """test TypeAlternativeForm"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_form(self):
        """test ParametersForm"""
        data = {'user':self.usertest, 'type_alternative':'Ac'}
        form = TypeAlternativeForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())


class test_activityform(TestCase):
    """test ActivityForm"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_form(self):
        """test ActivityForm"""
        data = {'user':self.usertest, 'type_activity':'Sp', 'activity':'Course à pied'}
        form = ActivityForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())

class test_substitutform(TestCase):
    """test SubstitutForm"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_form(self):
        """test SubstitutForm"""
        data = {'user':self.usertest, 'substitut':'PAST', 'nicotine':2.0}
        form = SubstitutForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())
