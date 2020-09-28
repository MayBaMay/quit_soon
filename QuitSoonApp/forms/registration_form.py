#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)

"""User registration form"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username, email and
    password.
    """
    email = forms.EmailField(required=True)

    def clean_email(self):
        """clean email field, check if email already used"""
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre utilisateur")
        return data

    def save(self, commit=True):
        """Save user registered"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
