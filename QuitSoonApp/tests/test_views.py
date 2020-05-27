from decimal import Decimal
import datetime

from django.test import TransactionTestCase, TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from QuitSoonApp.views import (
    index, today,
    register_view, login_view,
    profile, new_name, new_email, new_password, new_parameters,
    suivi, objectifs,
    paquets, smoke,
    alternatives, health,
)
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)
from QuitSoonApp.forms import PaquetFormCreation


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
        self.assertRedirects(response, '/today/', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertTrue(User.objects.filter(username='NewUserTest').exists())
        self.assertTrue(User.objects.get(username='NewUserTest').is_authenticated)

    def test_register_smoke_user(self):
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

    def test_register_smoke_email(self):
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

class LoginClientTestCase(TransactionTestCase):
    """
    Tests on Login view
    """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'loginTestUser', 'test@test.com', 'testpassword')

    def test_get_login_view(self):
        response = self.client.get(reverse('QuitSoonApp:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(auth.get_user(self.client), 'AnonymousUser')

    def test_login_succes_with_email(self):
        """Test client login with success"""
        self.assertTrue(auth.get_user(self.client), 'AnonymousUser')
        data = {'username':'test@test.com',
                'password':'testpassword'}
        response = self.client.post(reverse('QuitSoonApp:login'),
                                    data=data,
                                    follow=True)
        self.assertRedirects(response, '/today/', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertTrue(User.objects.filter(username='loginTestUser').exists())
        self.assertTrue(User.objects.get(username='loginTestUser').is_authenticated)
        user = User.objects.get(username='loginTestUser')
        self.assertTrue(auth.get_user(self.client), user)

    def test_login_succes_with_username(self):
        """Test client login with success"""
        self.assertTrue(auth.get_user(self.client), 'AnonymousUser')
        data = {'username':'loginTestUser',
                'password':'testpassword'}
        response = self.client.post(reverse('QuitSoonApp:login'),
                                    data=data,
                                    follow=True)
        self.assertRedirects(response, '/today/', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertTrue(User.objects.filter(username='loginTestUser').exists())
        self.assertTrue(User.objects.get(username='loginTestUser').is_authenticated)
        user = User.objects.get(username='loginTestUser')
        self.assertTrue(auth.get_user(self.client), user)

    def test_login_wrong_email(self):
        """Test client login failing wrong email"""
        self.assertTrue(auth.get_user(self.client), 'AnonymousUser')
        data = {'username':'wrong_email@test.com',
                'password':'testpassword'}
        response = self.client.post(reverse('QuitSoonApp:login'),
                         data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='wrongemail@test.com').exists())
        self.assertTrue(auth.get_user(self.client), 'AnonymousUser')
        self.assertRaises(ValidationError)


    def test_login_wrong_password(self):
        """Test client login failing wrong email"""
        self.assertTrue(auth.get_user(self.client), 'AnonymousUser')
        data = {'username':'test@test.com',
                'password':'wrongpassword'}
        response = self.client.post(reverse('QuitSoonApp:login'),
                         data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(auth.get_user(self.client), 'AnonymousUser')
        self.assertRaises(ValidationError)


class UserProfileTestCase(TransactionTestCase):
    """Tests on views and features related with user profile"""

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            username='Test', email='test@test.com', password='testpassword')

    def test_profile_get_newuser(self):
        self.client.login(username=self.user.username, password='testpassword')
        response = self.client.get(reverse('QuitSoonApp:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/profile.html')
        self.assertEqual(response.context['userprofile'], 'undefined')

    def test_profile_get_anonymoususer(self):
        response = self.client.get(reverse('QuitSoonApp:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/profile.html')
        self.assertEqual(response.context['userprofile'], None)

    def test_profile_get_existing_profile_user(self):
        userprofile = UserProfile.objects.create(
            user=self.user,
            date_start='2012-12-12',
            starting_nb_cig=3
        )
        self.client.login(username=self.user.username, password='testpassword')
        response = self.client.get(reverse('QuitSoonApp:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/profile.html')
        self.assertEqual(response.context['userprofile'], userprofile)

    def test_new_name(self):
        """test change nameview"""
        self.client.login(username=self.user.username, password='testpassword')
        user_id = self.user.id
        data = {'username':'NewName'}
        self.client.post(reverse('QuitSoonApp:new_name'),
                         data=data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(User.objects.filter(username="NewName").exists(), True)
        self.assertEqual(User.objects.filter(username="NewName").count(), 1)
        self.assertEqual(User.objects.get(id=user_id).username, 'NewName')
        self.client.logout()

    def test_new_name_already_in_db(self):
        """test change nameview with integrity error, name already in DB"""
        self.client.login(username=self.user.username, password='testpassword')
        User.objects.create_user(
            username='userinDB', email='Test@…', password='password')
        user_id = self.user.id
        username = self.user.username
        data = {'username':'userinDB'}
        self.client.post(reverse('QuitSoonApp:new_name'),
                         data=data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(User.objects.get(id=user_id).username, username)
        self.assertTrue(User.objects.get(username='userinDB').id != user_id)
        self.client.logout()

    def test_new_email(self):
        """test change nameview"""
        user_id = self.user.id
        self.client.login(username=self.user.username, password='testpassword')
        data = {'email':'New@email.test'}
        self.client.post(reverse('QuitSoonApp:new_email'),
                         data=data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(User.objects.get(id=user_id).email, 'New@email.test')
        self.client.logout()

    def test_new_email_already_in_db(self):
        """test change nameview with integrity error, name already in DB"""
        User.objects.create_user(
            username='userinDB', email='emailalreadyindb@test.com', password='password')
        user_id = self.user.id
        email = self.user.email
        self.client.login(username=self.user.username, password='testpassword')
        data = {'email':'emailalreadyindb@test.com'}
        self.client.post(reverse('QuitSoonApp:new_email'),
                         data=data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(User.objects.get(id=user_id).email, email)
        self.client.logout()

    def test_new_password_success(self):
        """test userpage view in post method"""
        self.client.login(username='Test', password='testpassword')
        data = {
            'old_password': 'testpassword',
            'new_password1': 'mynewpassword',
            'new_password2': 'mynewpassword',
        }
        self.client.post(reverse('QuitSoonApp:new_password'),
                         data=data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(User.objects.get(username="Test").check_password("mynewpassword"), True)
        self.client.logout()

    def test_new_password_fail_no_confirmed(self):
        """test userpage view in post method"""
        self.client.login(username='Test', password='testpassword')
        data = {
            'old_password': 'testpassword',
            'new_password1': 'mynewpassword',
            'new_password2': 'newpassword',
            }
        self.client.post(reverse('QuitSoonApp:new_password'),
                         data=data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(User.objects.get(username="Test").check_password("mynewpassword"), False)
        self.assertEqual(User.objects.get(username="Test").check_password("testpassword"), True)
        self.client.logout()

    def test_new_password_fail_too_short(self):
        """test userpage view in post method"""
        self.client.login(username='Test', password='testpassword')
        data = {
            'old_password': 'testpassword',
            'new_password1': 'secret',
            'new_password2': 'secret',
            }
        self.client.post(reverse('QuitSoonApp:new_password'),
                         data=data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(User.objects.get(username="Test").check_password("secret"), False)
        self.assertEqual(User.objects.get(username="Test").check_password("testpassword"), True)
        self.client.logout()

    def test_new_parameters_get(self):
        response = self.client.post(reverse('QuitSoonApp:new_parameters'))
        self.assertEqual(response.status_code, 200)

    def test_new_parameters_post(self):
        self.client.login(username='Test', password='testpassword')
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())
        data = {
            'date_start': '2020-05-17',
            'starting_nb_cig': 20,
            }
        self.client.post(reverse('QuitSoonApp:new_parameters'),
                         data=data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        self.assertEqual(UserProfile.objects.get(user=self.user).date_start, datetime.date(2020, 5, 17))
        self.assertEqual(UserProfile.objects.get(user=self.user).starting_nb_cig, 20)


class smokeAndhealthHabitsParametersTestCase(TestCase):
    """
    Tests on parameters pages, health (alternatives) or smoke (packs)
    """

    def setUp(self):
        """setup tests"""
        self.user = User.objects.create_user(
            'TestUser', 'test@test.com', 'testpassword')
        self.client.login(username=self.user.username, password='testpassword')

    def test_paquets_view_get(self):
        """Test get paquets view"""
        response = self.client.get(reverse('QuitSoonApp:paquets'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/paquets.html')

    def test_paquets_view_post_succes(self):
        """Test client post a form with success"""
        data = {'type_cig':'IND',
                'brand':'Camel',
                'qt_paquet':'20',
                'price':'10'}
        response = self.client.post(reverse('QuitSoonApp:paquets'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/paquets.html')
        db_pack = Paquet.objects.filter(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        self.assertTrue(db_pack.exists())
        self.assertEqual(db_pack[0].unit, 'U')
        self.assertEqual(db_pack[0].g_per_cig, None)

    def test_paquets_view_post_fails(self):
        """Test client post a form with invalid datas"""
        brandtest = Paquet.objects.create(
            user=self.user,
            type_cig='GR',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        datas = {'type_cig':'GR',
                'brand':'BRANDTEST',
                'qt_paquet':'50',
                'price':'30'}
        response = self.client.post(reverse('QuitSoonApp:paquets'),
                                    data=datas)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/paquets.html')
        db_pack = Paquet.objects.filter(
            user=self.user,
            type_cig='GR',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        self.assertEqual(db_pack.count(), 1)
        self.assertEqual(db_pack[0].id, brandtest.id)

    def test_delete_pack_views(self):
        """Test client post delete_pack view"""
        db_pack = Paquet.objects.create(
            user=self.user,
            type_cig='GR',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        response = self.client.post(reverse(
            'QuitSoonApp:delete_pack',
            args=[db_pack.id]))
        self.assertEqual(response.status_code, 302)
        filter = Paquet.objects.filter(
            user=self.user,
            type_cig='GR',
            brand='BRANDTEST',
            qt_paquet=50,
            price=30,
            )
        self.assertFalse(filter.exists())

    def test_change_g_per_cig_view(self):
        """Test client post hange_g_per_cig view"""
        pack = Paquet.objects.create(
            user=self.user,
            type_cig='PIPE',
            brand='BRANDTEST',
            qt_paquet=40,
            price=100,
            )
        self.assertEqual(pack.g_per_cig, None)
        data = {'type_cig':'PIPE',
                'brand':'BRANDTEST',
                'qt_paquet':'40',
                'price':'100',
                'g_per_cig':'1.1'
                }
        response = self.client.post(reverse('QuitSoonApp:change_g_per_cig'),
                                    data=data)
        paquet = Paquet.objects.get(
            id=pack.id,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(paquet.g_per_cig, Decimal('1.1'))
        self.assertEqual(paquet.price_per_cig, Decimal('2.75'))

    def test_smoke_get_no_pack(self):
        """ test get smoke view with no pack saved by user """
        response = self.client.get(reverse('QuitSoonApp:smoke'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['packs'].exists())
        self.assertFalse(response.context['smoke'].exists())

    def test_smoke_get_form(self):
        """ test get smoke view with packs saved by user, get form"""
        db_pack_ind = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        response = self.client.get(reverse('QuitSoonApp:smoke'))
        self.assertTrue(response.context['packs'].exists())
        self.assertFalse(response.context['smoke'].exists())
        self.assertTrue('form' in response.context)

    def test_smoke_post_validform_given_true(self):
        """ test post smoke view with given=True """
        db_pack_ind = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='NEW BRAND',
            qt_paquet=20,
            price=11,
            )
        data = {
            'date_smoke':datetime.date(2020, 5, 26),
            'time_smoke':datetime.time(12, 56),
            'type_cig_field':'IND',
            'indus_pack_field':db_pack_ind.id,
            'given_field':True,
            }
        response = self.client.post(reverse('QuitSoonApp:smoke'),
                                    data=data)
        filter_smoke = ConsoCig.objects.filter(
            user=self.user,
        )
        self.assertTrue(filter_smoke.exists())
        self.assertEqual(filter_smoke.count(), 1)

    def test_smoke_post_validform_given_false(self):
        """ test post smoke view with given=false """
        db_pack_ind = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        db_pack_ind2 = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='PHILIP MORRIS',
            qt_paquet=20,
            price=10.2,
            )
        db_pack_rol = Paquet.objects.create(
            user=self.user,
            type_cig='ROL',
            brand='1637',
            qt_paquet=30,
            price=12,
            )
        db_pack_nb = Paquet.objects.create(
            user=self.user,
            type_cig='NB',
            brand='beedies',
            qt_paquet=30,
            price=5,
            )
        data = {
            'date_smoke':datetime.date(2020, 5, 26),
            'time_smoke':datetime.time(12, 56),
            'type_cig_field':'IND',
            'indus_pack_field':db_pack_ind.id,
            'rol_pack_field':db_pack_rol.id,
            'nb_pack_field':db_pack_nb.id,
            'given_field':False,
            }
        response = self.client.post(reverse('QuitSoonApp:smoke'), data=data)
        filter_smoke = ConsoCig.objects.filter(
            user=self.user,
        )
        self.assertTrue(filter_smoke.exists())
        self.assertEqual(filter_smoke.count(), 1)

    def test_delete_smoke_fail(self):
        """ test get delete_smoke view with unexisting ConsoCig """
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[40]))
        self.assertEqual(response.status_code, 404)

    def test_delete_smoke_given_true(self):
        """ test get delete_smoke smoke.given=True """
        db_smoke_given = ConsoCig.objects.create(
            user=self.user,
            date_cig=datetime.date(2020, 5, 17),
            time_cig=datetime.time(13, 15),
            paquet=None,
            given=True,
            )
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[db_smoke_given.id]))
        self.assertEqual(response.status_code, 302)
        filter_conso = ConsoCig.objects.filter(user=self.user, id=db_smoke_given.id)
        self.assertFalse(filter_conso.exists())

    def test_delete_smoke_given_false(self):
        """ test get delete_smoke smoke.given=False """
        db_pack = Paquet.objects.create(
            user=self.user,
            type_cig='IND',
            brand='CAMEL',
            qt_paquet=20,
            price=10,
            )
        db_smoke_given = ConsoCig.objects.create(
            user=self.user,
            date_cig=datetime.date(2020, 5, 17),
            time_cig=datetime.time(13, 15),
            paquet=db_pack,
            given=False,
            )
        id = db_smoke_given.id
        response = self.client.post(reverse(
            'QuitSoonApp:delete_smoke',
            args=[db_smoke_given.id]))
        self.assertEqual(response.status_code, 302)
        filter_conso = ConsoCig.objects.filter(user=self.user, id=id)
        self.assertFalse(filter_conso.exists())

    def test_alternatives_view_post_succes_alt(self):
        """Test client post a form with alternatives with success"""
        data = {'type_alternative':'Ac',
                'type_activity':'Sp',
                'activity':'Course à pied'}
        response = self.client.post(reverse('QuitSoonApp:alternatives'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/alternatives.html')
        db_alternative = Alternative.objects.filter(
            user=self.user,
            type_alternative='Ac',
            type_activity='Sp',
            activity='COURSE À PIED',
            )
        self.assertTrue(db_alternative.exists())

    def test_alternatives_view_post_succes_subs(self):
        """Test client post a form with alternatives with success"""
        data = {'type_alternative':'Su',
                'substitut':'P24',
                'nicotine':'2',
                }
        response = self.client.post(reverse('QuitSoonApp:alternatives'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/alternatives.html')
        db_alternative = Alternative.objects.filter(
            user=self.user,
            type_alternative='Su',
            substitut='P24',
            nicotine='2',
            )
        self.assertTrue(db_alternative.exists())

    def test_alternatives_view_post_fails_unique(self):
        """Test client post a form with alternatives fails because of IntegrityError"""
        Alternative.objects.create(
            user=self.user,
            type_alternative='Su',
            substitut='GS',
            nicotine='2',
            )
        data = {'type_alternative':'Su',
                'substitut':'GS',
                'nicotine':'2',
                }
        response = self.client.post(reverse('QuitSoonApp:alternatives'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/alternatives.html')
        db_alternative = Alternative.objects.filter(
            user=self.user,
            type_alternative='Su',
            substitut='GS',
            nicotine='2',
            )
        self.assertTrue(db_alternative.count(), 1)

    def test_alternatives_view_post_get_only_relevant_form(self):
        """Test client post a form with alternatives with success"""
        data = {'type_alternative':'Su',
                'type_activity':'P16',
                'activity':'Course',
                'substitut':'P16',
                'nicotine':'2',
                }
        response = self.client.post(reverse('QuitSoonApp:alternatives'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'QuitSoonApp/alternatives.html')
        db_alternative = Alternative.objects.filter(
            user=self.user,
            type_alternative='Su',
            substitut='P16',
            nicotine='2',
            )
        self.assertTrue(db_alternative.exists())

    def test_delete_alternative_views_activity(self):
        """Test client post delete_alternative view with activity datas"""
        db_alternative = Alternative.objects.create(
            user=self.user,
            type_alternative='Ac',
            type_activity='So',
            activity='tabacologue',
            )
        response = self.client.post(reverse('QuitSoonApp:delete_alternative', args=[db_alternative.id]))
        self.assertEqual(response.status_code, 302)
        filter_alternative = Alternative.objects.filter(
            user=self.user,
            type_alternative='Ac',
            type_activity='So',
            activity='tabacologue',
            )
        self.assertFalse(filter_alternative.exists())

    def test_delete_alternative_views_substitut(self):
        """Test client post delete_alternative view with substitut datas"""
        db_alternative = Alternative.objects.create(
            user=self.user,
            type_alternative='Su',
            substitut='GM',
            nicotine=None,
            )
        response = self.client.post(reverse('QuitSoonApp:delete_alternative', args=[db_alternative.id]))
        self.assertEqual(response.status_code, 302)
        filter_alternative = Alternative.objects.filter(
            user=self.user,
            type_alternative='Su',
            type_activity='GM',
            activity=None,
            )
        self.assertFalse(filter_alternative.exists())

    def test_delete_alternative_views_substitut_used_in_ConsoAlternative(self):
        """Test client post delete_alternative view with substitut datas while used in ConsoAlternative"""
        db_alternative = Alternative.objects.create(
            user=self.user,
            type_alternative='Su',
            substitut='GM',
            nicotine=None,
            )
        conso = ConsoAlternative.objects.create(
            user=self.user,
            date_alter=datetime.date(2020, 5, 13),
            time_alter=datetime.time(13, 55),
            alternative=db_alternative,
        )
        filter_conso = ConsoAlternative.objects.filter(
            user=self.user,
            alternative=db_alternative,
            )
        self.assertTrue(filter_conso.exists())
        response = self.client.post(reverse('QuitSoonApp:delete_alternative', args=[db_alternative.id]))
        self.assertEqual(response.status_code, 302)
        filter_alternative = Alternative.objects.filter(
            user=self.user,
            type_alternative='Su',
            substitut='GM',
            nicotine=None,
            )
        self.assertTrue(filter_alternative.exists())
        self.assertEqual(filter_alternative[0].display, False)
