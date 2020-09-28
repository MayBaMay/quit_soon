#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code


"""tests index and legals views """


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class IndexViewTestCase(TestCase):
    """test index view"""

    def test_index_with_anonymous_user(self):
        """test anonymousUser acces to index"""
        response = self.client.get(reverse('QuitSoonApp:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_index_for_authenticated_user(self):
        """test index for authenticated user"""
        usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.client.login(username=usertest.username, password='arandompassword')
        response = self.client.get(reverse('QuitSoonApp:index'))
        self.assertEqual(response.status_code, 302)


class LegalsViewTestCase(TestCase):
    """test legals view"""

    def test_legals_with_anonymous_user(self):
        """test anonymousUser acces to legals"""
        response = self.client.get(reverse('QuitSoonApp:legals'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'legals.html')
        self.assertEqual(response.context['header_template_name'], 'base_header.html')

    def test_legals_for_authenticated_user(self):
        """test legals for authenticated user"""
        usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.client.login(username=usertest.username, password='arandompassword')
        response = self.client.get(reverse('QuitSoonApp:legals'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'legals.html')
        self.assertEqual(response.context['header_template_name'], 'QuitSoonApp/base_header.html')
