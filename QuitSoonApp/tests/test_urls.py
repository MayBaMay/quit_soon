"""urls.py tests"""
from django.test import SimpleTestCase
from django.urls import resolve, reverse

from QuitSoonApp.views import (
    index, today,
    register_view, login_view,
    profile, new_name, new_email, new_password, new_parameters,
    suivi, objectifs,
    paquets, delete_pack, bad, bad_history,
    alternatives, good, good_history,
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


    def test_today_url_is_resolved(self):
        """test today"""
        url = reverse('QuitSoonApp:today')
        self.assertEqual(resolve(url).func, today)

    def test_suivi_url_is_resolved(self):
        """test suivi"""
        url = reverse('QuitSoonApp:suivi')
        self.assertEqual(resolve(url).func, suivi)

    def test_objectifs_url_is_resolved(self):
        """test objectifs"""
        url = reverse('QuitSoonApp:objectifs')
        self.assertEqual(resolve(url).func, objectifs)


    def test_paquets_url_is_resolved(self):
        """test paquets"""
        url = reverse('QuitSoonApp:paquets')
        self.assertEqual(resolve(url).func, paquets)

    def test_delete_pack_url_is_resolved(self):
        """test delete_pack"""
        url = reverse('QuitSoonApp:delete_pack', args=['type_cig', 'brand', 20, 3.3])
        self.assertEqual(resolve(url).func, delete_pack)

    def test_bad_url_is_resolved(self):
        """test bad"""
        url = reverse('QuitSoonApp:bad')
        self.assertEqual(resolve(url).func, bad)

    def test_bad_history_url_is_resolved(self):
        """test bad_history"""
        url = reverse('QuitSoonApp:bad_history')
        self.assertEqual(resolve(url).func, bad_history)


    def test_alternatives_url_is_resolved(self):
        """test alternatives"""
        url = reverse('QuitSoonApp:alternatives')
        self.assertEqual(resolve(url).func, alternatives)

    def test_good_url_is_resolved(self):
        """test good"""
        url = reverse('QuitSoonApp:good')
        self.assertEqual(resolve(url).func, good)

    def test_good_history_url_is_resolved(self):
        """test good_history"""
        url = reverse('QuitSoonApp:good_history')
        self.assertEqual(resolve(url).func, good_history)
