from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from QuitSoonApp.forms import RegistrationForm, LoginForm
from django.contrib.auth.models import User




class test_registration(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")

    def test_valid_data(self):
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

    def test_blank_data(self):
        form = RegistrationForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'username': ['Ce champ est obligatoire.'],
            'email': ['Ce champ est obligatoire.'],
            'password1': ['Ce champ est obligatoire.'],
            'password2': ['Ce champ est obligatoire.'],
        })

    def test_username_already_in_db(self):
        data = {'username':'arandomname',
                'email':'newemail@test.com',
                'password1':'t3stpassword',
                'password2':'t3stpassword'}
        form = RegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

    def test_email_already_in_db(self):
        self.assertTrue(User.objects.filter(email='random@email.com'))
        data = {'username':'newuser',
                'email':'random@email.com',
                'password1':'t3stpassword',
                'password2':'t3stpassword'}
        form = RegistrationForm(data)
        # self.assertFalse(form.is_valid())
        # self.assertRaises(ValidationError)
