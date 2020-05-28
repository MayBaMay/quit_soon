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
        initial=False,
        label="J'ai taxé ma clope",
        widget=forms.CheckboxInput()
    )

    type_cig_field = forms.ChoiceField(
        required=True,
        choices=[],
        widget=forms.Select
        (attrs={'class':"form-control showtypes"}),
        label='',
        )

    def return_select():
        return forms.ChoiceField(
            required=False,
            choices=[],
            widget=forms.Select
            (attrs={'class':"form-control hide"}),
            label='',
            )

    indus_pack_field = return_select()
    rol_pack_field = return_select()
    cigares_pack_field = return_select()
    pipe_pack_field = return_select()
    nb_pack_field = return_select()
    gr_pack_field = return_select()

    def __init__(self, user, *args, **kwargs):

        self.user = user
        super(SmokeForm, self).__init__(*args, **kwargs)

        self.user_packs = Paquet.objects.filter(user=self.user, display=True)
        self.user_conso = ConsoCig.objects.filter(user=self.user)
        self.lastsmoke = self.last_smoke

        TYPE_CHOICES = []
        for pack in self.user_packs.order_by('type_cig').distinct('type_cig'):
            TYPE_CHOICES.append((pack.type_cig, pack.get_type_cig_display))
            if pack.type_cig == self.lastsmoke.type_cig:
                self.initial['type_cig_field'] = (pack.type_cig, pack.get_type_cig_display)
        TYPE_CHOICES = tuple(TYPE_CHOICES)


        self.fields['type_cig_field'].choices = TYPE_CHOICES

        INDUS_CHOICES = self.config_field('IND')
        self.fields['indus_pack_field'].choices = INDUS_CHOICES

        ROL_CHOICES = self.config_field('ROL')
        self.fields['rol_pack_field'].choices = ROL_CHOICES

        CIGARES_CHOICES = self.config_field('CIGARES')
        self.fields['cigares_pack_field'].choices = CIGARES_CHOICES

        PIPE_CHOICES = self.config_field('PIPE')
        self.fields['pipe_pack_field'].choices = PIPE_CHOICES

        NB_CHOICES = self.config_field('NB')
        self.fields['nb_pack_field'].choices = NB_CHOICES

        GR_CHOICES = self.config_field('GR')
        self.fields['gr_pack_field'].choices = GR_CHOICES

    @property
    def last_smoke(self):
        if self.user_conso:
            lastsmoke = self.user_conso.last().paquet
            if lastsmoke:
                return lastsmoke
            else:
                # get the last cig not given
                for conso in self.user_conso.order_by('-date_cig', '-time_cig'):
                    if conso.paquet:
                        return conso.paquet
                    else:
                        pass
                return Paquet.objects.filter(user=self.user)[0]
        else:
            return Paquet.objects.filter(user=self.user)[0]


    def config_field(self, type):
        type_cig_conf_dict = {
            'IND': 'indus_pack_field',
            'ROL': 'rol_pack_field',
            'CIGARES': 'cigares_pack_field',
            'PIPE': 'pipe_pack_field',
            'NB': 'nb_pack_field',
            'GR': 'gr_pack_field',
        }
        CHOICES = []
        for pack in self.user_packs.filter(type_cig=type):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            CHOICES.append((pack.id, display))
            if pack.brand == self.lastsmoke.brand and pack.qt_paquet == self.lastsmoke.qt_paquet:
                self.initial[type_cig_conf_dict[type]] = (pack.id, display)
        return tuple(CHOICES)

class HealthForm(forms.Form):

    date_health = forms.DateField(
        required=True,
        label='Date',
        widget=forms.DateInput(
            attrs={'class':"form-control currentDate",
                    'type':'date'},
    ))

    time_health = forms.TimeField(
        required=True,
        label='Heure',
        widget=forms.DateInput
            (attrs={'class':"form-control currentTime",
                    'type':'time'},
    ))

    duration_hour = forms.IntegerField(
        required=True,
        label="Pendant:",
    )

    type_alternative_field = forms.ChoiceField(
        required=True,
        choices=[],
        widget=forms.Select
        (attrs={'class':"form-control showtypes"}),
        label='',
        )

    def return_select():
        return forms.ChoiceField(
            required=False,
            choices=[],
            widget=forms.Select
            (attrs={'class':"form-control hide"}),
            label='',
            )

    type_activity_field = return_select()
    activity = return_select()
    type_substitut_field = return_select()
    substitut = return_select()

    def __init__(self, user, *args, **kwargs):

        self.user = user
        super(HealthForm, self).__init__(*args, **kwargs)

        self.user_alternatives = Alternative.objects.filter(user=self.user, display=True)
        self.user_conso = ConsoAlternative.objects.filter(user=self.user)
        self.lastalternative = self.last_alternative


        TYPE_CHOICES = [('Ac', 'Activité'), ('Su', 'Substitut')]
        self.fields['type_alternative_field'].choices = TYPE_CHOICES

        TYPE_ACTIVITY = self.config_field('Sp')
        self.fields['type_activity_field'].choices = TYPE_ACTIVITY

        ROL_CHOICES = self.config_field('ROL')
        self.fields['rol_pack_field'].choices = ROL_CHOICES

        CIGARES_CHOICES = self.config_field('CIGARES')
        self.fields['cigares_pack_field'].choices = CIGARES_CHOICES

        PIPE_CHOICES = self.config_field('PIPE')
        self.fields['pipe_pack_field'].choices = PIPE_CHOICES

        NB_CHOICES = self.config_field('NB')
        self.fields['nb_pack_field'].choices = NB_CHOICES

        GR_CHOICES = self.config_field('GR')
        self.fields['gr_pack_field'].choices = GR_CHOICES

    @property
    def last_alternative(self):
        if self.user_conso:
            lastalternative = self.user_conso.last().alternative
            if lastalternative:
                return lastalternative
            else:
                # get the last cig not given
                for conso in self.user_conso.order_by('-date_alter', '-time_alter'):
                    if conso.alternative:
                        return conso.alternative
                    else:
                        pass
                return Alternative.objects.filter(user=self.user)[0]
        else:
            return Alternative.objects.filter(user=self.user)[0]


    def config_field(self, type):
        type_cig_conf_dict = {
            'IND': 'indus_pack_field',
            'ROL': 'rol_pack_field',
            'CIGARES': 'cigares_pack_field',
            'PIPE': 'pipe_pack_field',
            'NB': 'nb_pack_field',
            'GR': 'gr_pack_field',
        }
        CHOICES = []
        for pack in self.user_packs.filter(type_cig=type):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            CHOICES.append((pack.id, display))
            if pack.brand == self.lastsmoke.brand and pack.qt_paquet == self.lastsmoke.qt_paquet:
                self.initial[type_cig_conf_dict[type]] = (pack.id, display)
        return tuple(CHOICES)
