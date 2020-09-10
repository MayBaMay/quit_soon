#!/usr/bin/env python

import datetime
from datetime import timedelta
import pytz

from django.utils import timezone
from django.utils.timezone import make_aware
from django import forms
from django.core.exceptions import ValidationError

from QuitSoonApp.models import Paquet, ConsoCig

from .base_user_related_forms import UserRelatedModelForm


class PaquetForm(UserRelatedModelForm):

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


class ChoosePackForm(forms.Form):
    type_cig_field = forms.ChoiceField(
        required=True,
        choices=[],
        widget=forms.Select
        (attrs={'class':"form-control"}),
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

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChoosePackForm, self).__init__(*args, **kwargs)

        self.user_packs = Paquet.objects.filter(user=self.user, display=True)
        self.user_conso = ConsoCig.objects.filter(user=self.user)
        self.lastsmoke = self.last_smoke

        TYPE_CHOICES = []
        for pack in self.user_packs.order_by('type_cig').distinct('type_cig'):
            TYPE_CHOICES.append((pack.type_cig, pack.get_type_cig_display))
            if pack.type_cig == self.lastsmoke.type_cig:
                self.initial['type_cig_field'] = (pack.type_cig, pack.get_type_cig_display)
        self.fields['type_cig_field'].choices = TYPE_CHOICES

        IND_CHOICES = self.config_field('ind_pack_field', 'IND')
        self.fields['ind_pack_field'].choices = IND_CHOICES

        ROL_CHOICES = self.config_field('rol_pack_field', 'ROL')
        self.fields['rol_pack_field'].choices = ROL_CHOICES

    @property
    def last_smoke(self):
        """get user last smoke or last created pack"""
        if self.user_conso:
            lastsmoke = self.user_conso.last().paquet
            if lastsmoke:
                return lastsmoke
            else:
                # get the last cig not given
                for conso in self.user_conso.order_by('-datetime_cig'):
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

class ChoosePackFormWithEmptyFields(ChoosePackForm):
    """
    Form displaying packs already used by user in order to filter consCig displayed in smoke_list
    """

    def __init__(self, user, *args, **kwargs):
        ChoosePackForm.__init__(self, user)
        super(ChoosePackFormWithEmptyFields, self).__init__(user, *args, **kwargs)

        TYPE_CHOICES = []
        for conso in self.user_conso.order_by('paquet__type_cig').distinct('paquet__type_cig'):
            # if conso not given cig (none pack)
            if conso.paquet:
                TYPE_CHOICES.append((conso.paquet.type_cig, conso.paquet.get_type_cig_display))
            else:
                if ('given', 'Clopes taxées') not in TYPE_CHOICES:
                    TYPE_CHOICES.append(('given', 'Clopes taxées'))
        TYPE_CHOICES.insert(0, ('empty', '------------------'))
        self.initial['type_cig_field'] = ('empty', '------------------')
        self.fields['type_cig_field'].choices = TYPE_CHOICES

        IND_CHOICES = self.config_field('ind_pack_field', 'IND')
        self.fields['ind_pack_field'].choices = IND_CHOICES

        ROL_CHOICES = self.config_field('rol_pack_field', 'ROL')
        self.fields['rol_pack_field'].choices = ROL_CHOICES

    def config_field(self, field, type):
        """configurate field depending of type_cig"""
        CHOICES = []
        used_pack = self.user_conso.order_by('paquet').distinct('paquet')
        for conso in used_pack:
            if not conso.given:
                if conso.paquet.type_cig == type:
                    display = "{} /{}{}".format(conso.paquet.brand, conso.paquet.qt_paquet, conso.paquet.unit)
                    CHOICES.append((conso.paquet.id, display))
        CHOICES.insert(0, ('empty', '------------------'))
        self.initial[field] = ('empty', '------------------')
        return tuple(CHOICES)

class SmokeForm(ChoosePackForm):
    """Class generating a form for user smoking action"""

    def __init__(self, user, tz_offset, *args, **kwargs):
        self.user = user
        self.tz_offset = tz_offset
        super(SmokeForm, self).__init__(user, *args, **kwargs)

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
        widget=forms.TimeInput
            (attrs={'class':"form-control currentTime",
                    'type':'time'},
    ))

    given_field = forms.BooleanField(
        required=False,
        initial=False,
        label="J'ai taxé ma clope",
        widget=forms.CheckboxInput()
    )

    def clean(self):
        cleaned_data = super(SmokeForm, self).clean()
        date = cleaned_data.get('date_smoke')
        time = cleaned_data.get('time_smoke')

        try:
            current_tz = timezone.get_current_timezone()
            # get datetime and now() user in utc
            dt_form = datetime.datetime.combine(date, time, tzinfo=pytz.utc) + timedelta(minutes=self.tz_offset)
            user_now = timezone.now()
            # get both variable in current timezone in order to compare dates
            dt_form = current_tz.normalize(dt_form.astimezone(current_tz))
            user_now = current_tz.normalize(user_now.astimezone(current_tz))

            if dt_form.date() > user_now.date():
                raise forms.ValidationError("Vous ne pouvez pas enregistrer de craquage pour les jours à venir")

        except TypeError:
            raise forms.ValidationError("Données temporelles incorrectes")

        return cleaned_data
