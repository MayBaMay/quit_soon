#!/usr/bin/env python

""" Forms related to Alternative or ConsoAlternative models """

from django import forms

from QuitSoonApp.models import Alternative, ConsoAlternative
from .base_forms import (
    UserRelatedModelForm, type_field, date_field, time_field,
    item_field, tomorrow_input,
    )


class TypeAlternativeForm(UserRelatedModelForm):
    """TypeAlternativ choice form"""

    class Meta:
        model = Alternative
        fields = ['type_alternative']
        labels = {'type_alternative': "Type d'alternative"}


class ActivityForm(UserRelatedModelForm):
    """Activity choice form"""

    class Meta:
        model = Alternative
        fields = ['type_activity', 'activity']
        labels = {
            'type_activity': "Type d'activité",
            'activity': 'Activité'
        }

    def clean_activity(self):
        """clean activity field"""
        data = self.cleaned_data['activity']
        return data.upper()


class SubstitutForm(UserRelatedModelForm):
    """Substitut choice form"""

    class Meta:
        model = Alternative
        fields = ['substitut', 'nicotine']
        labels = {
            'substitut': "Substituts",
            'nicotine': 'Nicotine (mg)'
        }


class ChooseAlternativeForm(forms.Form):
    """Alternative choice form"""

    type_alternative_field = type_field

    sp_field = item_field()
    so_field = item_field()
    lo_field = item_field()
    su_field = item_field()

    def __init__(self, user, *args, **kwargs):

        self.user = user
        super().__init__(*args, **kwargs)

        self.user_alternatives = Alternative.objects.filter(user=self.user, display=True)
        self.user_conso = ConsoAlternative.objects.filter(user=self.user)

        #########################################################################################
        # define type alternative configuration (choices + initial)
        # choices = Sport, Loisir, Soin, Substitut (if alternatives of this types saved by user)
        # initial = last alternative type_activity or last alternative type_alternative(if =='Su')
        #########################################################################################
        type_alternative_choices = []
        user_conso_type = self.user_alternatives.filter(type_alternative='Ac')
        ordered_user_conso_type = user_conso_type.order_by('type_activity')
        for alternative in ordered_user_conso_type.distinct('type_activity'):
            # include user activity types
            type_alternative_choices.append(
                (alternative.type_activity, alternative.get_type_activity_display)
                )
            if alternative.type_activity == self.last_alternative().type_activity:
                self.initial['type_alternative_field'] = (
                    alternative.type_activity,
                    alternative.get_type_activity_display
                    )
        # if user has substituts, choice substitut
        if Alternative.objects.filter(user=self.user, type_alternative='Su'):
            type_alternative_choices.append(('Su', 'Substitut'))
        if self.last_alternative().type_alternative == 'Su':
            self.initial['type_alternative_field'] = ('Su', 'Substitut')
        # define type_alternative_choices
        type_alternative_choices = tuple(type_alternative_choices)
        self.fields['type_alternative_field'].choices = type_alternative_choices

        #########################################################################################
        # define type fields configuration (choices + initial)
        #########################################################################################

        sp_field_choices = self.config_field('sp_field', 'Ac', 'Sp')
        self.fields['sp_field'].choices = sp_field_choices

        so_field_choices = self.config_field('so_field', 'Ac', 'So')
        self.fields['so_field'].choices = so_field_choices

        lo_field_choices = self.config_field('lo_field', 'Ac', 'Lo')
        self.fields['lo_field'].choices = lo_field_choices

        su_field_choices = self.config_field('su_field', 'Su')
        self.fields['su_field'].choices = su_field_choices

    def filter_conso(self, type_alternative, type_activity):
        """Filter ConsoAlternative depending on type_alternative or type_activity"""
        if type_alternative == 'Su':
            return self.user_conso.filter(alternative__type_alternative=type_alternative)
        if type_alternative == 'Ac':
            return self.user_conso.filter(alternative__type_activity=type_activity)
        return self.user_conso

    def last_alternative(self, type_alternative=None, type_activity=None):
        """get user last healthy action or last created alternative"""
        conso = self.filter_conso(type_alternative, type_activity)
        if conso:
            lastalternative = conso.last().alternative
            if lastalternative:
                return lastalternative
        filter_alternative = self.user_alternatives
        if type_alternative:
            filter_alternative = self.user_alternatives.filter(
                type_alternative=type_alternative
                )
        if type_activity:
            filter_alternative = self.user_alternatives.filter(
                type_activity=type_activity
                )
        return filter_alternative.last()

    def config_field(self, field_name, type_alternative, type_activity=None):
        """
        configurate field depending on:
            type_activity if type_alternative='Ac' (get one field for each type of activity)
            type_alternative if type_alternative='Su' (get all substitutes in one field)
        """
        choices = []
        if type_alternative == 'Ac':
            for alternative in self.user_alternatives.filter(type_activity=type_activity):
                choices.append((alternative.id, alternative.activity))
                last_alternative_activity = self.last_alternative(
                    type_alternative, type_activity
                    ).activity
                if alternative.activity == last_alternative_activity:
                    self.initial[field_name] = (alternative.id, alternative.activity)
        if type_alternative == 'Su':
            for alternative in self.user_alternatives.filter(type_alternative=type_alternative):
                display = "{} ({}mg)".format(
                    alternative.get_substitut_display(),
                    alternative.nicotine
                    )
                choices.append((alternative.id, display))
                if alternative.substitut == self.last_alternative(type_alternative).substitut:
                    if alternative.nicotine == self.last_alternative(type_alternative).nicotine:
                        self.initial[field_name] = (alternative.id, display)
        return tuple(choices)


class ChooseAlternativeFormWithEmptyFields(ChooseAlternativeForm):
    """
    Form displaying packs already used by user in order to filter consCig displayed in smoke_list
    """
    def __init__(self, user, *args, **kwargs):
        ChooseAlternativeForm.__init__(self, user)
        super().__init__(user, *args, **kwargs)

        #########################################################################################
        # define type alternative configuration (choices + initial)
        # choices = Sport, Loisir, Soin, Substitut (if alternatives of this types saved by user)
        # initial = empty '------------------'
        #########################################################################################
        type_alternative_choices = []
        user_conso_type = self.user_conso.filter(alternative__type_alternative='Ac')
        ordered_user_conso_type = user_conso_type.order_by('alternative__type_activity')
        for conso in ordered_user_conso_type.distinct('alternative__type_activity'):
            # include user activity types
            type_alternative_choices.append(
                (conso.alternative.type_activity, conso.alternative.get_type_activity_display)
                )
        # if user has substituts, choice substitut
        if self.user_conso.filter(alternative__type_alternative='Su'):
            type_alternative_choices.append(('Su', 'Substitut'))
        type_alternative_choices.insert(0, ('empty', '------------------'))
        self.initial['type_alternative_field'] = ('empty', '------------------')
        # define type_alternative_choices
        type_alternative_choices = tuple(type_alternative_choices)
        self.fields['type_alternative_field'].choices = type_alternative_choices

        #########################################################################################
        # define type fields configuration (choices + initial)
        #########################################################################################

        sp_field_choices = self.config_field('sp_field', 'Ac', 'Sp')
        self.fields['sp_field'].choices = sp_field_choices

        so_field_choices = self.config_field('so_field', 'Ac', 'So')
        self.fields['so_field'].choices = so_field_choices

        lo_field_choices = self.config_field('lo_field', 'Ac', 'Lo')
        self.fields['lo_field'].choices = lo_field_choices

        su_field_choices = self.config_field('su_field', 'Su')
        self.fields['su_field'].choices = su_field_choices

    def config_field(self, field_name, type_alternative, type_activity=None):
        """
        configurate field depending on:
            type_activity if type_alternative='Ac' (get one field for each type of activity)
            type_alternative if type_alternative='Su' (get all substitutes in one field)
        """
        choices = []
        if type_alternative == 'Ac':
            choices.insert(0, ('empty', '------------------'))
            self.initial[field_name] = ('empty', '------------------')
            user_conso_type = self.user_conso.filter(alternative__type_activity=type_activity)
            ordered_user_conso_type = user_conso_type.order_by('alternative__activity')
            for conso in ordered_user_conso_type.distinct('alternative__activity'):
                choices.append((conso.alternative.id, conso.alternative.activity))
        if type_alternative == 'Su':
            choices.insert(0, ('empty', '------------------'))
            self.initial[field_name] = ('empty', '------------------')
            user_conso_type = self.user_conso.filter(alternative__type_alternative=type_alternative)
            ordered_user_conso_type = user_conso_type.order_by('alternative__substitut')
            for conso in ordered_user_conso_type.distinct('alternative__substitut'):
                display = "{} ({}mg)".format(
                    conso.alternative.get_substitut_display(),
                    conso.alternative.nicotine)
                choices.append((conso.alternative.id, display))
        return tuple(choices)

class HealthForm(ChooseAlternativeForm):
    """Class generating a form for user healthy action"""

    def __init__(self, user, tz_offset, *args, **kwargs):
        self.user = user
        self.tz_offset = tz_offset
        super().__init__(user, *args, **kwargs)


    date_health = date_field

    time_health = time_field

    duration_hour = forms.IntegerField(
        required=False,
        label="h",
        widget=forms.Select
            (attrs={'class':"form-control show"},
             choices= [tuple([x,x]) for x in range(25)]),
    )

    duration_min = forms.IntegerField(
        required=False,
        label='m',
        widget=forms.Select
            (attrs={'class':"form-control show"},
             choices= [tuple([x,x]) for x in range(0, 60, 5)]),
    )

    def clean(self):
        """Clean all_field and specialy make sure total duration in not none for activities"""
        cleaned_data = super().clean()
        date = cleaned_data.get('date_health')
        time = cleaned_data.get('time_health')
        duration_hour = cleaned_data.get('duration_hour')
        duration_min = cleaned_data.get('duration_min')
        type_alternative = cleaned_data.get('type_alternative_field')

        # check if duration for user activiy
        if not duration_hour and not duration_min and type_alternative != 'Su':
            raise forms.ValidationError(
                "Vous n'avez pas renseigné de durée pour cette activité"
                )

        if tomorrow_input(date, time, self.tz_offset):
            raise forms.ValidationError(
                "Vous ne pouvez pas enregistrer d'action saine pour les jours à venir"
                )


        return cleaned_data
