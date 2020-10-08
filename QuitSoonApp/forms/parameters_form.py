#!/usr/bin/env python

""" User change parameters form """

from django import forms

from QuitSoonApp.models import Paquet
from .base_forms import (
    date_field,
    )


class ParametersForm(forms.Form):
    """A form for user to define smoking habits when starting using app"""

    date_start = date_field

    starting_nb_cig = forms.IntegerField(
        required=True,
        label='',
        widget=forms.Select
            (attrs={'class':"form-control show"},
             choices= [tuple([x,x]) for x in range(0, 100)]),
    )

    ref_pack = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select
        (attrs={'class':"form-control"}),
        label='',
        )

    def __init__(self, user, *args, **kwargs):

        self.user = user
        super().__init__(*args, **kwargs)
        user_packs = Paquet.objects.filter(user=self.user, display=True)
        choices = []
        for pack in user_packs:
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            choices.append((pack.id, display))
        choices = tuple(choices)
        self.fields['ref_pack'].choices = choices
