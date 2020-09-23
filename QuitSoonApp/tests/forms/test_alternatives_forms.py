#!/usr/bin/env python

from django.test import TestCase
from django.contrib.auth.models import User

from QuitSoonApp.forms import (
    TypeAlternativeForm,
    ActivityForm,
    SubstitutForm
    )
from QuitSoonApp.models import Alternative
from ..MOCK_DATA import BaseTestCase

class test_TypeAlternativeForm(BaseTestCase):
    """test TypeAlternativeForm"""

    def setUp(self):
        """setup tests"""
        super().setUp()

    def test_form(self):
        """test ParametersForm"""
        data = {'user':self.usertest, 'type_alternative':'Ac'}
        form = TypeAlternativeForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())


class test_ActivityForm(BaseTestCase):
    """test ActivityForm"""

    def setUp(self):
        """setup tests"""
        super().setUp()

    def test_form(self):
        """test ActivityForm"""
        data = {'user':self.usertest, 'type_activity':'Sp', 'activity':'Course à pied'}
        form = ActivityForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())

class test_SubstitutForm(BaseTestCase):
    """test SubstitutForm"""

    def setUp(self):
        """setup tests"""
        super().setUp()

    def test_form(self):
        """test SubstitutForm"""
        data = {'user':self.usertest, 'substitut':'PAST', 'nicotine':2.0}
        form = SubstitutForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())
