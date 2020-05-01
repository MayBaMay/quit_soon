"""urls.py tests"""
from django.test import SimpleTestCase
from django.urls import resolve, reverse

from ..views import (
    index,
    register_view, login_view,
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
