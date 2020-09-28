#!/usr/bin/env python
# pylint: disable=W0212
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code


"""tests reset password by user """

from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core import mail

class ResetPasswordTransactionTestCase(TransactionTestCase):
    """Test reset password feature"""

    def setUp(self):
        """setup tests"""
        self.user1 = User.objects.create_user(
            'registerTestUser', 'test@test.com', 'testpassword')

    def test_reset_password(self):
        """test reset password view in get method"""

        # get password_reset
        response = self.client.get(reverse('QuitSoonApp:password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

        # post password_reset wrong email
        response = self.client.post('/password_reset/', {'email': 'not_a_real_email@email.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

        # post password_reset email found
        response = self.client.post(reverse('password_reset'), {'email': 'test@test.com'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/accounts/password_reset/done/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        print(mail.outbox)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("http://", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].subject, 'NicotineKill réinitialisation du mot de passe')
        # test redirect to password_reset_done
        self.assertRedirects(response, '/accounts/password_reset/done/')

        # get password_reset_confirm
        uid = response.context[0]['uid']
        url = mail.outbox[0].body.split('http://testserver')[1].split('\n', 1)[0]
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/reset/'+uid+'/set-password/')

        # post valid password_reset_confirm
        data = {'new_password1': 'newpasswordforTest',
                'new_password2': 'newpasswordforTest'}
        response = self.client.post('/accounts/reset/'+uid+'/set-password/', data=data)
        self.assertEqual(response.status_code, 302)
        # test redirect to password_reset_complete
        self.assertRedirects(response, '/accounts/reset/done/')

        self.assertTrue(
            get_user_model()._default_manager.get().check_password('newpasswordforTest')
            )
