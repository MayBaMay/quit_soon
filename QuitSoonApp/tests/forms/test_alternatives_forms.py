#!/usr/bin/env python
# pylint: disable=C0103 #Method name "test_smokeForm_is_valid" doesn't conform to snake_case naming style (invalid-name)
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)
# pylint: disable=duplicate-code

"""test Forms related to Alternative model"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options

from QuitSoonApp.models import (
    UserProfile,
    Alternative
    )
from QuitSoonApp.forms import (
    TypeAlternativeForm,
    ActivityForm,
    SubstitutForm
    )


class test_typealternativeForm(TestCase):
    """test TypeAlternativeForm"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_form(self):
        """test ParametersForm"""
        data = {'user':self.usertest, 'type_alternative':'Ac'}
        form = TypeAlternativeForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())


class test_activityform(TestCase):
    """test ActivityForm"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_form(self):
        """test ActivityForm"""
        data = {'user':self.usertest, 'type_activity':'Sp', 'activity':'Course à pied'}
        form = ActivityForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())


class test_substitutform(TestCase):
    """test SubstitutForm"""

    def setUp(self):
        """setup tests"""
        self.usertest = User.objects.create_user(
            username="arandomname",
            email="random@email.com",
            password="arandompassword"
            )

    def test_form(self):
        """test SubstitutForm"""
        data = {'user':self.usertest, 'substitut':'PAST', 'nicotine':2.0}
        form = SubstitutForm(self.usertest, data=data)
        self.assertTrue(form.is_valid())


class AlternativesFormStaticLiveServerTestCase(StaticLiveServerTestCase):
    """Test Alternatives Form changing depending on choices user"""

    @classmethod
    def setUpClass(cls):
        """setup tests"""
        super().setUpClass()
        options = Options()
        options.headless = True
        cls.browser = WebDriver(options=options)
        cls.browser.implicitly_wait(100)

    @classmethod
    def tearDownClass(cls):
        """teardown tests"""
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        """setup tests"""
        super().setUp()
        self.user = User.objects.create(username='johnDo', email='test@test.com', is_active=True)
        self.user.set_password('mot2passe5ecret')
        self.user.save()
        UserProfile.objects.create(
            user=self.user,
            date_start='2020-05-13',
            starting_nb_cig=20
        )
        self.login()

    def login(self):
        """login user in selenium driver"""
        self.browser.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.browser.find_element_by_name("username")
        username_input.send_keys('johnDo')
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys('mot2passe5ecret')
        self.browser.find_element_by_xpath('//input[@type="submit"]').click()

    def test_change_choice_type_alternative(self):
        """test user change option type_alternative"""
        self.browser.get(self.live_server_url + '/alternatives/')
        self.assertFalse(
            self.browser.find_element_by_css_selector("#id_substitut").is_displayed()
            )
        self.assertFalse(
            self.browser.find_element_by_css_selector("#id_nicotine").is_displayed()
            )
        self.assertTrue(
            self.browser.find_element_by_css_selector("#id_type_activity").is_displayed()
            )
        self.assertTrue(
            self.browser.find_element_by_css_selector("#id_activity").is_displayed()
            )
        self.browser.find_element_by_xpath(
            "//select[@id='id_type_alternative']/option[@value='Su']"
            ).click()
        self.assertTrue(
            self.browser.find_element_by_css_selector("#id_substitut").is_displayed()
            )
        self.assertTrue(
            self.browser.find_element_by_css_selector("#id_nicotine").is_displayed()
            )
        self.assertFalse(
            self.browser.find_element_by_css_selector("#id_type_activity").is_displayed()
            )
        self.assertFalse(
            self.browser.find_element_by_css_selector("#id_activity").is_displayed()
            )
        self.browser.find_element_by_xpath(
            "//select[@id='id_type_alternative']/option[@value='Ac']"
            ).click()
        self.assertFalse(
            self.browser.find_element_by_css_selector("#id_substitut").is_displayed()
            )
        self.assertFalse(
            self.browser.find_element_by_css_selector("#id_nicotine").is_displayed()
            )
        self.assertTrue(
            self.browser.find_element_by_css_selector("#id_type_activity").is_displayed()
            )
        self.assertTrue(
            self.browser.find_element_by_css_selector("#id_activity").is_displayed()
            )

    def test_save_Su_alternative(self):
        """save substitut alternative"""
        self.browser.get(self.live_server_url + '/alternatives/')
        self.browser.find_element_by_xpath(
            "//select[@id='id_type_alternative']/option[@value='Su']"
            ).click()
        self.browser.find_element_by_xpath(
            "//select[@id='id_substitut']/option[@value='PAST']"
            ).click()
        self.browser.find_element_by_css_selector("#id_nicotine").send_keys(2)
        self.browser.find_element_by_xpath(
            "//input[@type='submit']"
        ).click()
        self.assertTrue(Alternative.objects.filter(
            user=self.user,
            type_alternative='Su',
            substitut='PAST',
            nicotine=2
            ).exists())

    def test_save_Ac_alternative(self):
        """save activity alternative"""
        self.browser.get(self.live_server_url + '/alternatives/')
        self.browser.find_element_by_xpath(
            "//select[@id='id_type_alternative']/option[@value='Ac']"
            ).click()
        self.browser.find_element_by_xpath(
            "//select[@id='id_type_activity']/option[@value='Sp']"
            ).click()
        self.browser.find_element_by_css_selector("#id_activity").send_keys("vélo")
        self.browser.find_element_by_xpath(
            "//input[@type='submit']"
        ).click()
        self.assertTrue(Alternative.objects.filter(
            user=self.user,
            type_alternative='Ac',
            type_activity='Sp',
            activity="VÉLO"
            ).exists())
