#!/usr/bin/env python

""" Forms related to Paquet or ConsoCig models """

from django import forms

from QuitSoonApp.models import Paquet, ConsoCig
from .base_forms import (
    UserRelatedModelForm, type_field, date_field, time_field,
    item_field, tomorrow_input,
    )


class PaquetForm(UserRelatedModelForm):
    """Paquet choice form"""

    def clean_brand(self):
        """clean field brand, make upper"""
        data = self.cleaned_data['brand']
        return data.upper()


class PaquetFormCreation(PaquetForm):
    """A form for user to create a new smoking usual pack"""

    class Meta:
        model = Paquet
        fields = ['type_cig', 'brand', 'qt_paquet', 'price']
        labels = {
            'type_cig': 'Type de cigarettes',
            'brand': 'Marque',
            'qt_paquet':'Nombre par paquet',
            'price':' Prix du paquet'
        }

    def clean(self):
        cleaned_data = super().clean()
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
    """Change paquet g/cig form"""

    class Meta:
        model = Paquet
        fields = ['type_cig', 'brand', 'qt_paquet', 'price', 'g_per_cig']


class ChoosePackForm(forms.Form):
    """Paquet choice form"""
    type_cig_field = type_field

    ind_pack_field = item_field()
    rol_pack_field = item_field()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        self.user_packs = Paquet.objects.filter(user=self.user, display=True)
        self.user_conso = ConsoCig.objects.filter(user=self.user)
        self.lastsmoke = self.last_smoke

        type_choices = []
        for pack in self.user_packs.order_by('type_cig').distinct('type_cig'):
            type_choices.append((pack.type_cig, pack.get_type_cig_display))
            if pack.type_cig == self.lastsmoke.type_cig:
                self.initial['type_cig_field'] = (pack.type_cig, pack.get_type_cig_display)
        self.fields['type_cig_field'].choices = type_choices

        ind_choices = self.config_field('ind_pack_field', 'IND')
        self.fields['ind_pack_field'].choices = ind_choices

        rol_choices = self.config_field('rol_pack_field', 'ROL')
        self.fields['rol_pack_field'].choices = rol_choices

    @property
    def last_smoke(self):
        """get user last smoke or last created pack"""
        if self.user_conso:
            lastsmoke = self.user_conso.last().paquet
            if lastsmoke:
                return lastsmoke
            # get the last cig not given
            for conso in self.user_conso.order_by('-datetime_cig'):
                if conso.paquet:
                    return conso.paquet
            return Paquet.objects.filter(user=self.user, display=True).last()
        return Paquet.objects.filter(user=self.user, display=True).last()


    def config_field(self, field, type_cig):
        """configurate field depending of type_cig"""
        choices = []
        for pack in self.user_packs.filter(type_cig=type_cig):
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            choices.append((pack.id, display))
            if pack.brand == self.lastsmoke.brand and pack.qt_paquet == self.lastsmoke.qt_paquet:
                self.initial[field] = (pack.id, display)
        return tuple(choices)

class ChoosePackFormWithEmptyFields(ChoosePackForm):
    """
    Form displaying packs already used by user in order to filter consCig displayed in smoke_list
    """

    def __init__(self, user, *args, **kwargs):
        ChoosePackForm.__init__(self, user)
        super().__init__(user, *args, **kwargs)

        type_choices = []
        for conso in self.user_conso.order_by('paquet__type_cig').distinct('paquet__type_cig'):
            # if conso not given cig (none pack)
            if conso.paquet:
                type_choices.append((conso.paquet.type_cig, conso.paquet.get_type_cig_display))
            else:
                if ('given', 'Clopes taxées') not in type_choices:
                    type_choices.append(('given', 'Clopes taxées'))
        type_choices.insert(0, ('empty', '------------------'))
        self.initial['type_cig_field'] = ('empty', '------------------')
        self.fields['type_cig_field'].choices = type_choices

        ind_choices = self.config_field('ind_pack_field', 'IND')
        self.fields['ind_pack_field'].choices = ind_choices

        rol_choices = self.config_field('rol_pack_field', 'ROL')
        self.fields['rol_pack_field'].choices = rol_choices

    def config_field(self, field, type_cig):
        """configurate field depending of type_cig"""
        choices = []
        used_pack = self.user_conso.order_by('paquet').distinct('paquet')
        for conso in used_pack:
            if not conso.given:
                if conso.paquet.type_cig == type_cig:
                    display = "{} /{}{}".format(
                        conso.paquet.brand,
                        conso.paquet.qt_paquet,
                        conso.paquet.unit
                        )
                    choices.append((conso.paquet.id, display))
        choices.insert(0, ('empty', '------------------'))
        self.initial[field] = ('empty', '------------------')
        return tuple(choices)

class SmokeForm(ChoosePackForm):
    """Class generating a form for user smoking action"""

    def __init__(self, user, tz_offset, *args, **kwargs):
        self.user = user
        self.tz_offset = tz_offset
        super().__init__(user, *args, **kwargs)

    date_smoke = date_field

    time_smoke = time_field

    given_field = forms.BooleanField(
        required=False,
        initial=False,
        label="J'ai taxé ma clope",
        widget=forms.CheckboxInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date_smoke')
        time = cleaned_data.get('time_smoke')

        try:
            if tomorrow_input(date, time, self.tz_offset):
                raise forms.ValidationError(
                    "Vous ne pouvez pas enregistrer de craquage pour les jours à venir"
                    )
        except TypeError as error:
            raise forms.ValidationError("Données temporelles incorrectes") from error

        return cleaned_data
