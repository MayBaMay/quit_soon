from django.test import TransactionTestCase, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ..views import (
    register_view,
    login_view,
)



class RegisterClientTestCase(TestCase):
    """
    Tests on register view
    """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'registerTestUser', 'test@test.com', 'testpassword')

    def test_get_register_view(self):
        response = self.client.get(reverse('QuitSoonApp:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_succes(self):
        """Test client register with success"""
        data = {'username':'NewUserTest',
                'email':'testnewUser@test.com',
                'password1':'t3stpassword',
                'password2':'t3stpassword'}
        response = self.client.post(reverse('QuitSoonApp:register'),
                                    data=data,
                                    follow=True)
        self.assertTrue(response.redirect_chain, [('index.html', 302)])
        self.assertTrue(User.objects.filter(username='NewUserTest').exists())
        self.assertTrue(User.objects.get(username='NewUserTest').is_authenticated)

    def test_register_bad_user(self):
        """Test client register with success"""
        data = {'username':'registerTestUser',
                'email':'testnewUser@test.com',
                'password1':'t3stpassword',
                'password2':'t3stpassword'}
        response = self.client.post(reverse('QuitSoonApp:register'),
                         data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='registerTestUser').exists())
        self.assertFalse(User.objects.get(username='registerTestUser').email == 'testnewUser@test.com')
        self.assertRaises(ValidationError)


    def test_register_bad_email(self):
        """Test client register with success"""
        data = {'username':'NewUserTest',
                'email':'test@test.com',
                'password1':'t3stpassword',
                'password2':'t3stpassword'}
        response = self.client.post(reverse('QuitSoonApp:register'),
                         data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='NewUserTest').exists())
        self.assertRaises(ValidationError)

    def test_register_passwords_diff(self):
        """Test client register with success"""
        data = {'username':'NewUserTest',
                'email':'testnewUser@test.com',
                'password1':'t3stpassword',
                'password2':'t3stdsqfpassword'}
        response = self.client.post(reverse('QuitSoonApp:register'),
                         data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='NewUserTest').exists())
        self.assertRaises(ValidationError)

# class LoginClientTestCase(TransactionTestCase):
#     """
#     Tests on Login view
#     """
#
#     def setUp(self):
#         """setup tests"""
#         # self.user = User.objects.create_user(
#         #     'loginTestUser', 'test@test.com', 'testpassword')
#         # self.client.logout()
#         # self.assertTrue(User.objects.get(username='loginTestUser').is_authenticated)
#         self.factory = RequestFactory()
#         self.user = User.objects.create_user(
#             username='jacob', email='jacob@…', password='top_secret')
#
#     def test_get_login_view(self):
#         response = self.client.get(reverse('QuitSoonApp:login'))
#         self.assertEqual(response.status_code, 200)
#
#     def test_login_succes(self):
#         """Test client login with success"""
#         request = self.factory.get(reverse('QuitSoonApp:login'))
#         request.user = AnonymousUser()
#         request.data = {'username':'test@test.com',
#                         'password':'testpassword'}
#         response = login_view(request)
#         self.assertEqual(response.status_code, 200)
#
#         # data = {'username':'test@test.com',
#         #         'password':'testpassword'}
#         # response = self.client.post(reverse('QuitSoonApp:login'),
#         #                  data=data,
#         #                  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#         # self.assertEqual(response.status_code, 200)
#         # self.assertTrue(User.objects.filter(username='loginTestUser').exists())
#         # self.assertTrue(User.objects.get(username='loginTestUser').is_authenticated)
#         # self.assertJSONEqual(
#         #     str(response.content, encoding='utf8'),
#         #     {'response': 'success'}
#         # )
#         # self.client.logout()
#
#     def test_login_wrong_email(self):
#         """Test client login failing wrong email"""
#         data = {'username':'wrong_email@test.com',
#                 'password':'testpassword'}
#         response = self.client.post(reverse('QuitSoonApp:login'),
#                          data=data,
#                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(User.objects.filter(email='wrongemail@test.com').exists())
#         # self.assertJSONEqual(
#         #     str(response.content, encoding='utf8'),
#         #     {'response': 'error-user-none"'}
#         # )
#         # self.client.logout()
#
#     def test_login_wrong_password(self):
#         """Test client login failing wrong email"""
#         data = {'username':'test@test.com',
#                 'password':'wrongpassword'}
#         response = self.client.post(reverse('QuitSoonApp:login'),
#                          data=data,
#                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#         self.assertEqual(response.status_code, 200)
#         # self.assertJSONEqual(
#         #     str(response.content, encoding='utf8'),
#         #     {'response': 'wrong_password"'}
#         # )
#         # self.client.logout()
