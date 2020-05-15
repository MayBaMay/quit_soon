"""urls.py tests"""
from django.test import SimpleTestCase
from django.urls import resolve, reverse

from QuitSoonApp.views import (
    index, today,
    register_view, login_view,
    profile, paquets, alternatives,
    suivi, objectifs,
    new_name, new_email, new_password, new_parameters,
)

class TestUrls(SimpleTestCase):
    """test on urls.py with SimpleTestCase class"""

    def test_index_url_is_resolved(self):
        """test index_url"""
        url = reverse('QuitSoonApp:index')
        self.assertEqual(resolve(url).func, index)

    def test_register_view_url_is_resolved(self):
        """test register_view"""
        url = reverse('QuitSoonApp:register')
        self.assertEqual(resolve(url).func, register_view)

    def test_login_url_is_resolved(self):
        """test login_url"""
        url = reverse('QuitSoonApp:login')
        self.assertEqual(resolve(url).func, login_view)

    def test_today_url_is_resolved(self):
        """test today"""
        url = reverse('QuitSoonApp:today')
        self.assertEqual(resolve(url).func, today)

    def test_paquets_url_is_resolved(self):
        """test paquets"""
        url = reverse('QuitSoonApp:paquets')
        self.assertEqual(resolve(url).func, paquets)

    def test_alternatives_url_is_resolved(self):
        """test alternatives"""
        url = reverse('QuitSoonApp:alternatives')
        self.assertEqual(resolve(url).func, alternatives)

    def test_suivi_url_is_resolved(self):
        """test suivi"""
        url = reverse('QuitSoonApp:suivi')
        self.assertEqual(resolve(url).func, suivi)

    def test_objectifs_url_is_resolved(self):
        """test objectifs"""
        url = reverse('QuitSoonApp:objectifs')
        self.assertEqual(resolve(url).func, objectifs)
        

    def test_profile_url_is_resolved(self):
        """test today"""
        url = reverse('QuitSoonApp:profile')
        self.assertEqual(resolve(url).func, profile)

    def test_new_name_url_is_resolved(self):
        """test new_name"""
        url = reverse('QuitSoonApp:new_name')
        self.assertEqual(resolve(url).func, new_name)

    def test_new_email_url_is_resolved(self):
        """test new_email"""
        url = reverse('QuitSoonApp:new_email')
        self.assertEqual(resolve(url).func, new_email)

    def test_new_password_url_is_resolved(self):
        """test new_password"""
        url = reverse('QuitSoonApp:new_password')
        self.assertEqual(resolve(url).func, new_password)

    def test_new_parameters_url_is_resolved(self):
        """test new_parameters"""
        url = reverse('QuitSoonApp:new_parameters')
        self.assertEqual(resolve(url).func, new_parameters)
