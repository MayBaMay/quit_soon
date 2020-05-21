from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from QuitSoonApp.forms import (
    RegistrationForm,
    ParametersForm,
    PaquetFormCreation,
    PaquetFormCustomGInCig,
    TypeAlternativeForm,
    ActivityForm,
    SubstitutForm
    )
from QuitSoonApp.models import UserProfile, Paquet, Alternative


class test_registration(TestCase):
    """test registration form"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")

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


class test_ParametersForm(TestCase):
    """test ParametersForm with smoking habits"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")

    def test_form(self):
        """test ParametersForm"""
        data = {'user':self.user, 'date_start':'2020-05-17', 'starting_nb_cig':'4'}
        form = ParametersForm(data=data)
        self.assertTrue(form.is_valid())

class test_PaquetFormCreation(TestCase):
    """test PaquetFormCreation"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")

    def test_PaquetFormCreation_is_valid(self):
        """test valid PaquetFormCreation"""
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10'}
        form = PaquetFormCreation(self.user, data)
        self.assertTrue(form.is_valid())

    def test_PaquetFormCreation_is_not_valid(self):
        """test invalid PaquetFormCreation, datas already in DB"""
        Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10'}
        form = PaquetFormCreation(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

class test_PaquetFormCustomGInCig(TestCase):
    """test PaquetFormCustomGInCig"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username="arandomname", email="random@email.com", password="arandompassword")


    def test_PaquetFormCustomGInCig_is_valid(self):
        """test valid PaquetFormCustomGInCig"""
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10',
                'g_per_cig':'0.9'}
        form = PaquetFormCustomGInCig(self.user, data)
        self.assertTrue(form.is_valid())


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


# class test_AlternativeForm(TestCase):
#
#     def setUp(self):
#         """setup tests"""
#         self.user = User.objects.create_user(
#             username="arandomname", email="random@email.com", password="arandompassword")
#
#     def test_AlternativeForm_is_valid(self):
#         """test valid AlternativeForm"""
#         data = {'type_alternative':'Sp',
#                 'alternative':'COURSE',}
#         form = AlternativeForm(self.user, data)
#         self.assertTrue(form.is_valid())
#
#     def test_AlternativeForm_is_valid_substitut(self):
#         """test valid AlternativeForm with substitut entry"""
#         data = {'type_alternative':'Su',
#                 'substitut':'P24',
#                 'nicotine':'2',
#                 }
#         form = AlternativeForm(self.user, data)
#         self.assertTrue(form.is_valid())
#
#     def test_AlternativeForm_is_valid_failed_clean_alternative(self):
#         """test in valid AlternativeForm pb clean_alternative"""
#         data = {'type_alternative':'Su',
#                 'alternative':'COURSE',
#                 }
#         form = AlternativeForm(self.user, data)
#         self.assertRaises(ValidationError)
#         self.assertTrue('alternative' in form.errors.as_data().keys())
#         self.assertFalse(form.is_valid())
#
#     def test_AlternativeForm_is_valid_failed_clean_substitut(self):
#         """test in valid AlternativeForm pb clean_substitut"""
#         data = {'type_alternative':'Sp',
#                 'alternative':'COURSE',
#                 'substitut':'PAST',
#                 }
#         form = AlternativeForm(self.user, data)
#         self.assertRaises(ValidationError)
#         self.assertTrue('substitut' in form.errors.as_data().keys())
#         self.assertFalse(form.is_valid())
#
#     def test_AlternativeForm_is_valid_failed_clean_nicotine(self):
#         """test in valid AlternativeForm pb clean_nicotine"""
#         data = {'type_alternative':'Sp',
#                 'alternative':'COURSE',
#                 'substitut':'PAST',
#                 'nicotine':'3',
#                 }
#         form = AlternativeForm(self.user, data)
#         self.assertRaises(ValidationError)
#         self.assertTrue('nicotine' in form.errors.as_data().keys())
#         self.assertFalse(form.is_valid())
#
#     def test_AlternativeForm_fail_validate_unicity(self):
#         first = Alternative.objects.create(
#             user=self.user,
#             type_alternative='Sp',
#             alternative='COURSE',
#         )
#         data = {'type_alternative':'Sp',
#                 'alternative':'COURSE',}
#         form = AlternativeForm(self.user, data)
#         self.assertRaises(ValidationError)
#         db_alternative = Alternative.objects.filter(
#             user=self.user,
#             type_alternative='Sp',
#             alternative='COURSE',
#             )
#         self.assertEqual(db_alternative.count(), 1)
#         self.assertEqual(first.id, db_alternative[0].id)
#
#     def test_AlternativeForm_fail_validate_unicity(self):
#         first = Alternative.objects.create(
#             user=self.user,
#             type_alternative='Sp',
#             alternative='COURSE',
#         )
#         data = {'type_alternative':'Sp',
#                 'alternative':'COURSE',
#                 'substitut':'',
#                 'nicotine':''}
#         form = AlternativeForm(self.user, data)
#         self.assertRaises(ValidationError)
#         db_alternative = Alternative.objects.filter(
#             user=self.user,
#             type_alternative='Sp',
#             alternative='COURSE',
#             )
#         self.assertEqual(db_alternative.count(), 1)
#         self.assertEqual(first.id, db_alternative[0].id)
