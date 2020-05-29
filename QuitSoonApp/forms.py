#!/usr/bin/env python

import unicodedata
import datetime

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
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
    """Class generating a form for user smoking action"""

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

    ind_pack_field = return_select()
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

        IND_CHOICES = self.config_field('ind_pack_field', 'IND')
        self.fields['ind_pack_field'].choices = IND_CHOICES

        ROL_CHOICES = self.config_field('rol_pack_field', 'ROL')
        self.fields['rol_pack_field'].choices = ROL_CHOICES

        CIGARES_CHOICES = self.config_field('cigares_pack_field', 'CIGARES')
        self.fields['cigares_pack_field'].choices = CIGARES_CHOICES

        PIPE_CHOICES = self.config_field('pipe_pack_field', 'PIPE')
        self.fields['pipe_pack_field'].choices = PIPE_CHOICES

        NB_CHOICES = self.config_field('nb_pack_field', 'NB')
        self.fields['nb_pack_field'].choices = NB_CHOICES

        GR_CHOICES = self.config_field('gr_pack_field', 'GR')
        self.fields['gr_pack_field'].choices = GR_CHOICES

    @property
    def last_smoke(self):
        """get user last smoke or last created pack"""
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
                return Paquet.objects.filter(user=self.user, display=True).last()
        else:
            return Paquet.objects.filter(user=self.user, display=True).last()


    def config_field(self, field, type):
        """configurate field depending of type_cig"""
        CHOICES = []
        for pack in self.user_packs.filter(type_cig=type):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            CHOICES.append((pack.id, display))
            if pack.brand == self.lastsmoke.brand and pack.qt_paquet == self.lastsmoke.qt_paquet:
                self.initial[field] = (pack.id, display)
        return tuple(CHOICES)


class HealthForm(forms.Form):
    """Class generating a form for user healthy action"""

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

    type_alternative_field = forms.ChoiceField(
        required=True,
        choices=[],
        widget=forms.Select
            (attrs={'class':"form-control"}),
        label='',
        )

    def alternative_field():
        return forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select
            (attrs={'class':"form-control hide"}),
        label='',
        )

    sp_field = alternative_field()
    so_field = alternative_field()
    lo_field = alternative_field()
    su_field = alternative_field()

    ecig_vape_or_start = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple
            (attrs={'class':"hide"},
             ),
        choices=[('V', "J'ai vapoté aujourd'hui"),
                 ('S', "J'ai démarré un nouveau flacon")],
        label='',
        )

    duration_hour = forms.IntegerField(
        required=False,
        label="Pendant:",
        widget=forms.Select
            (attrs={'class':"form-control show"},
             choices= [tuple([x,x]) for x in range(25)]),
    )

    duration_min = forms.IntegerField(
        required=False,
        label='',
        widget=forms.Select
            (attrs={'class':"form-control show"},
             choices= [tuple([x,x]) for x in range(0, 60, 5)]),
    )


    def __init__(self, user, *args, **kwargs):

        self.user = user
        super(HealthForm, self).__init__(*args, **kwargs)

        self.user_alternatives = Alternative.objects.filter(user=self.user, display=True)
        self.user_conso = ConsoAlternative.objects.filter(user=self.user)

        #########################################################################################
        # define type alternative configuration (choices + initial)
        # choices = Sport, Loisir, Soin, Substitut (if alternatives of this types saved by user)
        # initial = last alternative type_activity or last alternative type_alternative(if =='Su')
        #########################################################################################
        TYPE_ALTERNATIVE_CHOICES = []
        for alternative in self.user_alternatives.filter(type_alternative='Ac').order_by('type_activity').distinct('type_activity'):
            # include user activity types
            TYPE_ALTERNATIVE_CHOICES.append((alternative.type_activity, alternative.get_type_activity_display))
            if alternative.type_activity == self.last_alternative().type_activity:
                self.initial['type_alternative_field'] = (alternative.type_activity, alternative.get_type_activity_display)
        # if user has substituts, choice substitut
        if Alternative.objects.filter(user=self.user, type_alternative='Su'):
            TYPE_ALTERNATIVE_CHOICES.append(('Su', 'Substitut'))
        if self.last_alternative().type_alternative == 'Su':
            self.initial['type_alternative_field'] = ('Su', 'Substitut')
        # define type_alternative_choices
        TYPE_ALTERNATIVE_CHOICES = tuple(TYPE_ALTERNATIVE_CHOICES)
        self.fields['type_alternative_field'].choices = TYPE_ALTERNATIVE_CHOICES

        #########################################################################################
        # define type fields configuration (choices + initial)
        #########################################################################################

        SP_FIELD_CHOICES = self.config_field('sp_field', 'Ac', 'Sp')
        self.fields['sp_field'].choices = SP_FIELD_CHOICES

        SO_FIELD_CHOICES = self.config_field('so_field', 'Ac', 'So')
        self.fields['so_field'].choices = SO_FIELD_CHOICES

        LO_FIELD_CHOICES = self.config_field('lo_field', 'Ac', 'Lo')
        self.fields['lo_field'].choices = LO_FIELD_CHOICES

        SU_FIELD_CHOICES = self.config_field('su_field', 'Su')
        self.fields['su_field'].choices = SU_FIELD_CHOICES

    def last_alternative(self, type_alternative=None, type_activity=None):
        """get user last healthy action or last created alternative"""
        if type_alternative == 'Su':
            conso = self.user_conso.filter(alternative__type_alternative=type_alternative)
        elif type_alternative == 'Ac':
            conso = self.user_conso.filter(alternative__type_activity=type_activity)
        else:
            # get last conso unrelated to type
            conso = self.user_conso

        if conso:
            lastalternative = conso.last().alternative
            if lastalternative:
                return lastalternative
        else:
            filter = self.user_alternatives
            if type_alternative:
                filter = self.user_alternatives.filter(type_alternative=type_alternative)
            if type_activity:
                filter = self.user_alternatives.filter(type_activity=type_activity)
            return filter.last()

    def config_field(self, field_name, type_alternative, type_activity=None):
        """
        configurate field depending on:
            type_activity if type_alternative='Ac' (get one field for each type of activity)
            type_alternative if type_alternative='Su' (get all substitutes in one field)
        """
        CHOICES = []
        if type_alternative == 'Ac':
            for alternative in self.user_alternatives.filter(type_activity=type_activity):
                CHOICES.append((alternative.id, alternative.activity))
                if alternative.activity == self.last_alternative(type_alternative, type_activity).activity:
                    self.initial[field_name] = (alternative.id, alternative.activity)
            return tuple(CHOICES)
        elif type_alternative == 'Su':
            for alternative in self.user_alternatives.filter(type_alternative=type_alternative):
                display = "{} ({}mg)".format(alternative.get_substitut_display(), alternative.nicotine)
                CHOICES.append((alternative.id, display))
                if alternative.substitut == self.last_alternative(type_alternative).substitut and alternative.nicotine == self.last_alternative(type_alternative).nicotine:
                    self.initial[field_name] = (alternative.id, display)
            return tuple(CHOICES)
        else:
            return None

    def clean(self):
        """Clean all_field and specialy make sure total duration in not none for activities"""
        cleaned_data = super().clean()
        date_alter = cleaned_data.get('date_alter')
        duration_hour = cleaned_data.get('duration_hour')
        duration_min = cleaned_data.get('duration_min')
        type_alternative = cleaned_data.get('type_alternative_field')

        # check if duration for user activiy
        if not duration_hour and not duration_min and type_alternative != 'Su':
            raise forms.ValidationError("Vous n'avez pas renseigné de durée pour cette activité")

        try:
            ecig_data = cleaned_data.get('ecig_vape_or_start')

            id_subsitut = int(cleaned_data.get('su_field'))
            if type_alternative == 'Su':
                # if a Ecig substitut alternative is selected in su_field
                if id_subsitut:
                    if Alternative.objects.get(id=id_subsitut).substitut.upper() == 'ECIG':
                        # check if at least one choice has been selected
                        if ecig_data == []:
                            raise forms.ValidationError("""
                                Vous avez sélectionné la cigarette électronique,
                                indiquez si vous avez vapoté aujourd'hui et/ou si vous avez démarré un nouveau flacon.
                                Ceci nous permettra de calculer le dosage quotidien moyen de votre consommation de nicotine
                                """)
        except ValueError:
            pass
