import unicodedata

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _


class RegistrationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username, email and
    password.
    """
    email = forms.EmailField(required=True)

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre utilisateur")
        return data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    A form that login a user with either username and email and his password
    """
    def clean_username(self):
        data = self.cleaned_data['username']
        if not User.objects.filter(username=data).exists():
            if not User.objects.filter(email=data).exists():
                raise forms.ValidationError("Cet identifiant ne correspond à aucun utilisateur")
        return data

    def clean_password(self):
        username = self.cleaned_data.get('username')
        data = self.cleaned_data.get('password')

        if username is not None and data:
            if User.objects.filter(username=username).exists():
                self.user_cache = authenticate(self.request, username=username, password=data)
                if self.user_cache is None:
                    raise forms.ValidationError("Le mot de passe est invalide (attention aux majuscules et minuscules)")
        return data
