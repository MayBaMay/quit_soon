#!/usr/bin/env python

import unicodedata
import datetime

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _
from django.core.exceptions import NON_FIELD_ERRORS

from QuitSoonApp.models import UserProfile, Paquet, ConsoCig, Alternative, ConsoAlternative


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


class UserRelatedForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


class PaquetForm(UserRelatedForm):

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
            display=True,
            )
        if same_packs:
            raise forms.ValidationError("Vous avez déjà enregistré ce paquet")


class PaquetFormCustomGInCig(PaquetForm):

    class Meta:
        model = Paquet
        fields = ['type_cig', 'brand', 'qt_paquet', 'price', 'g_per_cig']


class TypeAlternativeForm(UserRelatedForm):

    class Meta:
        model = Alternative
        fields = ['type_alternative']


class ActivityForm(UserRelatedForm):

    class Meta:
        model = Alternative
        fields = ['type_activity', 'activity']

    def clean_activity(self):
        data = self.cleaned_data['activity']
        return data.upper()


class SubstitutForm(UserRelatedForm):

    class Meta:
        model = Alternative
        fields = ['substitut', 'nicotine']


class SmokeForm(forms.Form):

    date_smoke = forms.DateField(
        required=True,
        label='Date',
        widget=forms.DateInput(
            attrs={'class':"form-control currentDate",
                    'type':'date'},
    ))

    time_smoke = forms.TimeField(
        required=True,
        label='Heure',
        widget=forms.DateInput
            (attrs={'class':"form-control currentTime",
                    'type':'time'},
    ))

    given_field = forms.BooleanField(
        required=False,
        label="J'ai taxé ma clope",
        widget=forms.CheckboxInput()
    )

    def return_select():
        return forms.ChoiceField(
            required=True,
            choices=[],
            widget=forms.Select
            (attrs={'class':"form-control hide"}),
            label='',
            )

    type_cig_field = return_select()
    indus_pack_field = return_select()
    rol_pack_field = return_select()
    cigares_pack_field = return_select()
    pipe_pack_field = return_select()
    nb_pack_field = return_select()
    gr_pack_field = return_select()

    def __init__(self, user, *args, **kwargs):

        self.user = user
        super(SmokeForm, self).__init__(*args, **kwargs)

        user_packs = Paquet.objects.filter(user=self.user, display=True)
        user_conso = ConsoCig.objects.filter(user=self.user)

        if user_conso:
            lastsmoke = user_conso.last().paquet
            if lastsmoke == None:
                # get the last cig not given
                for conso in user_conso.order_by('date_cig', 'time_cig'):
                    if conso.paquet:
                        lastsmoke = conso.paquet
                # if still pack == None
                if not lastsmoke:
                    lastsmoke = Paquet.objects.filter(user=self.user)[0]
        else:
            lastsmoke = Paquet.objects.filter(user=self.user)[0]

        TYPE_CHOICES = []
        for pack in user_packs.order_by('type_cig').distinct('type_cig'):
            TYPE_CHOICES.append((pack.type_cig, pack.get_type_cig_display))
            if pack.type_cig == lastsmoke.type_cig:
                self.initial['type_cig_field'] = (pack.type_cig, pack.get_type_cig_display)
        TYPE_CHOICES = tuple(TYPE_CHOICES)

        self.fields['type_cig_field'].choices = TYPE_CHOICES

        INDUS_CHOICES = []
        for pack in user_packs.filter(type_cig='IND'):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            INDUS_CHOICES.append((pack.id, display))
            if pack.brand == lastsmoke.brand and pack.qt_paquet == lastsmoke.qt_paquet:
                self.initial['indus_pack_field'] = (pack.id, display)
        INDUS_CHOICES = tuple(INDUS_CHOICES)

        self.fields['indus_pack_field'].choices = INDUS_CHOICES

        ROL_CHOICES = []
        for pack in user_packs.filter(type_cig='ROL'):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            ROL_CHOICES.append((pack.id, display))
            if pack.brand == lastsmoke.brand and pack.qt_paquet == lastsmoke.qt_paquet:
                self.initial['rol_pack_field'] = (pack.id, display)
        ROL_CHOICES = tuple(ROL_CHOICES)

        self.fields['rol_pack_field'].choices = ROL_CHOICES

        CIGARES_CHOICES = []
        for pack in user_packs.filter(type_cig='CIGARES'):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            CIGARES_CHOICES.append((pack.id, display))
            if pack.brand == lastsmoke.brand and pack.qt_paquet == lastsmoke.qt_paquet:
                self.initial['cigares_pack_field'] = (pack.id, display)
        CIGARES_CHOICES = tuple(CIGARES_CHOICES)

        self.fields['cigares_pack_field'].choices = CIGARES_CHOICES

        PIPE_CHOICES = []
        for pack in user_packs.filter(type_cig='PIPE'):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            PIPE_CHOICES.append((pack.id, display))
            if pack.brand == lastsmoke.brand and pack.qt_paquet == lastsmoke.qt_paquet:
                self.initial['pipe_pack_field'] = (pack.id, display)
        PIPE_CHOICES = tuple(PIPE_CHOICES)

        self.fields['pipe_pack_field'].choices = PIPE_CHOICES

        NB_CHOICES = []
        for pack in user_packs.filter(type_cig='NB'):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            NB_CHOICES.append((pack.id, display))
            if pack.brand == lastsmoke.brand and pack.qt_paquet == lastsmoke.qt_paquet:
                self.initial['nb_pack_field'] = (pack.id, display)
        NB_CHOICES = tuple(NB_CHOICES)

        self.fields['nb_pack_field'].choices = NB_CHOICES

        GR_CHOICES = []
        for pack in user_packs.filter(type_cig='GR'):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            GR_CHOICES.append((pack.id, display))
            if pack.brand == lastsmoke.brand and pack.qt_paquet == lastsmoke.qt_paquet:
                self.initial['gr_pack_field'] = (pack.id, display)
        GR_CHOICES = tuple(GR_CHOICES)

        self.fields['gr_pack_field'].choices = GR_CHOICES
