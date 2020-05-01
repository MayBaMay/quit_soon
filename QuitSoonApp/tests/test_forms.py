from django.test import TestCase
from django.contrib.auth import get_user_model

from QuitSoonApp.forms import RegistrationForm, LoginForm
from django.contrib.auth.models import User


class RegistrationForm(TestCase):

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
        self.assertEqual(user.username, "Turanga Leela")
        self.assertEqual(user.email, "leela@example.com")
        self.assertEqual(user.body, "vqkjhvoqev04")
        self.assertEqual(user.check_password("vqkjhvoqev04"), True)

    # def test_blank_data(self):
    #     form = CommentForm({}, entry=self.entry)
    #     self.assertFalse(form.is_valid())
    #     self.assertEqual(form.errors, {
    #         'name': ['This field is required.'],
    #         'email': ['This field is required.'],
    #         'body': ['This field is required.'],
    #     })
    #
    # def test_url(self):
    #     title = "This is my test title"
    #     today = datetime.date.today()
    #     entry = Entry.objects.create(title=title, body="body",
    #                                  author=self.user)
    #     slug = slugify(title)
    #     url = "/{year}/{month}/{day}/{pk}-{slug}/".format(
    #         year=today.year,
    #         month=today.month,
    #         day=today.day,
    #         slug=slug,
    #         pk=entry.pk,
    #     )
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response,
    #                             template_name='blog/entry_detail.html')
    #
    # def test_misdated_url(self):
    #     entry = Entry.objects.create(
    #         title="title", body="body", author=self.user)
    #     url = "/0000/00/00/{0}-misdated/".format(entry.id)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(
    #         response, template_name='blog/entry_detail.html')
    #
    # def test_invalid_url(self):
    #     entry = Entry.objects.create(
    #         title="title", body="body", author=self.user)
    #     response = self.client.get("/0000/00/00/0-invalid/")
    #     self.assertEqual(response.status_code, 404)
