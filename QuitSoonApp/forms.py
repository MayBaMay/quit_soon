import unicodedata

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _

from QuitSoonApp.models import Paquet


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


class ParametersForm(forms.Form):
    date_start = forms.DateField()
    starting_nb_cig = forms.IntegerField()


class PaquetForm(forms.Form):

    class Meta:
        model = Paquet
        fields = ['type_cig', 'brand', 'qt_paquet', 'price']

    TYPE_CIG_CHOICES = [
        ('IND', 'Cigarettes industrielles'),
        ('ROL', 'Cigarettes roulées'),
        ('CIGARES', 'Cigares'),
        ('CIGARIOS', 'Cigarios'),
        ('PIPE', 'Pipe'),
        ('NB', 'Autres(en nb/paquet)'),
        ('GR', 'Autres(en g/paquet)'),
    ]

    type_cig = forms.CharField(label='Type', widget=forms.Select(choices=TYPE_CIG_CHOICES))
    brand = forms.CharField(label='Marque')
    qt_paquet = forms.IntegerField(label='Quantité')
    price = forms.DecimalField(label='Prix')
