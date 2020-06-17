#!/usr/bin/env python

from django import forms

from QuitSoonApp.models import Paquet

class ParametersForm(forms.Form):
    """A form for user to define smoking habits when starting using app"""

    date_start = forms.DateField(
        required=True,
        label='Date',
        widget=forms.DateInput(
            attrs={'class':"form-control currentDate",
                    'type':'date'},
            )
    )

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
        super(ParametersForm, self).__init__(*args, **kwargs)
        user_packs = Paquet.objects.filter(user=self.user, display=True)
        CHOICES = []
        for pack in user_packs:
            display = "{} /{}{}".format(pack.brand, pack.qt_paquet, pack.unit)
            CHOICES.append((pack.id, display))
        CHOICES = tuple(CHOICES)
        self.fields['ref_pack'].choices = CHOICES
