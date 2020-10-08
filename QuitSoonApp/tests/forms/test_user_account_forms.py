#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code


"""
Tests forms related to user informations:
RegistrationForm and ParametersForm
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from QuitSoonApp.forms import (
    RegistrationForm,
    EmailValidationOnResetPassword,
    ParametersForm,
    )
from QuitSoonApp.models import Paquet


class RegistrationTestCase(TestCase):
    """test registration form"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_valid_data(self):
        """test succes form"""
        data = {'username':'brandnewuser',
                'email':'test@test.com',
                'password1':'t3stpassword',
                'password2':'t3stpassword'}
        form = RegistrationForm(data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'brandnewuser')
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.check_password('t3stpassword'), True)
        self.assertTrue(user.is_authenticated)
        self.assertTrue(User.objects.filter(username='brandnewuser').exists())

    def test_blank_data(self):
        """test form with empty field"""
        form = RegistrationForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'username': ['Ce champ est obligatoire.'],
            'email': ['Ce champ est obligatoire.'],
            'password1': ['Ce champ est obligatoire.'],
            'password2': ['Ce champ est obligatoire.'],
        })

    def test_username_already_in_db(self):
        """test form with username already in DB"""
        data = {'username':'arandomname',
                'email':'newemail@test.com',
                'password1':'t3stpassword',
                'password2':'t3stpassword'}
        form = RegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

    def test_email_already_in_db(self):
        """test form with email already in DB"""
        self.assertTrue(User.objects.filter(email='random@email.com'))
        data = {'username':'newuser',
                'email':'random@email.com',
                'password1':'t3stpassword',
                'password2':'t3stpassword'}
        form = RegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)


class ParametersFormTestCase(TestCase):
    """test ParametersForm with smoking habits"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        self.pack = Paquet.objects.create(
        user=self.usertest,
        type_cig='IND',
        brand='CAMEL',
        qt_paquet=20,
        price=10,
        )
        self.pack2 = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='1637',
            qt_paquet=30,
            unit='G',
            price=12,
            )

    def test_form_get(self):
        """test get form with choices field"""
        form = ParametersForm(self.usertest)
        self.assertEqual(len(form.fields['ref_pack'].choices), 2)
        self.assertTrue((self.pack.id, 'CAMEL /20U') in form.fields['ref_pack'].choices)
        self.assertTrue((self.pack2.id, '1637 /30G') in form.fields['ref_pack'].choices)

    def test_form_post_first_connection(self):
        """test ParametersForm while request.POST include newpack creation"""
        newpack = Paquet.objects.create(
            user=self.usertest,
            type_cig='ROL',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            first=True,
            )
        data = {
            'date_start': '2020-05-17',
            'starting_nb_cig': 20,
            'type_cig':'ROL',
            'brand':'BRANDTEST',
            'qt_paquet':'50',
            'price':'30',
            'ref_pack': newpack.id
            }
        form = ParametersForm(self.usertest, data)
        self.assertTrue(form.is_valid())

    def test_form_post(self):
        """test ParametersForm"""
        data = {
            'date_start': '2020-06-04',
            'starting_nb_cig': '20',
            'packs': str(self.pack.id)
            }
        form = ParametersForm(self.usertest, data)
        self.assertTrue(form.is_valid())

    def test_form_post_missing_data(self):
        """test form with no data required fields"""
        form = ParametersForm(self.usertest, {})
        self.assertEqual(form.errors, {
            'date_start': ['Ce champ est obligatoire.'],
            'starting_nb_cig': ['Ce champ est obligatoire.'],
            })


class EmailValidationOnResetPasswordTestCase(TestCase):
    """test EmailValidationOnResetPassword """

    def test_email_reset_form_fail(self):
        """ test email reset form fail cause email not in db"""
        data = {"email": "not_a_real_email@email.com"}
        form = EmailValidationOnResetPassword(data)
        self.assertEqual(
            form.errors["email"], ["L'adresse renseignée ne correspond à aucun compte utilisateur"]
        )

    def test_email_reset_form_success(self):
        """test email reset form success"""
        User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )
        form = EmailValidationOnResetPassword("random@email.com")
        self.assertTrue(form.is_valid)
