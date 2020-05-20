import unicodedata

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _

from QuitSoonApp.models import UserProfile, Paquet


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


class ParametersForm(forms.ModelForm):
    """A form for user to define smoking habits when starting using app"""

    class Meta:
        model = UserProfile
        fields = ['date_start', 'starting_nb_cig']


class PaquetForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_brand(self):
        data = self.cleaned_data['brand']
        return data.upper()


class PaquetFormCreation(PaquetForm):
    """A form for user to create a new smoking usual pack"""

    class Meta:
        model = Paquet
        fields = ['type_cig', 'brand', 'qt_paquet', 'price']

    def clean(self):
        cleaned_data = super(PaquetFormCreation, self).clean()
        same_packs = Paquet.objects.filter(
            user=self.user,
            type_cig=cleaned_data.get('type_cig'),
            brand=cleaned_data.get('brand'),
            qt_paquet=cleaned_data.get('qt_paquet'),
            price=cleaned_data.get('price'),
            )
        if same_packs:
            raise forms.ValidationError("Vous avez déjà enregistré ce paquet")


class PaquetFormCustomGInCig(PaquetForm):

    class Meta:
        model = Paquet
        fields = ['type_cig', 'brand', 'qt_paquet', 'price', 'g_per_cig']
