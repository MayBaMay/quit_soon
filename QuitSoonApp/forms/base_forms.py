#!/usr/bin/env python

""" Base for Forms classes """

import datetime
from datetime import timedelta
import pytz

from django.utils import timezone
from django import forms


class UserRelatedModelForm(forms.ModelForm):
    """ Base Form classes depending on user """

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


type_field = forms.ChoiceField(
    required=True,
    choices=[],
    widget=forms.Select
        (attrs={'class':"form-control"}),
    label='',
    )

date_field = forms.DateField(
    required=True,
    label='Date',
    widget=forms.DateInput(
        attrs={'class':"form-control currentDate",
                'type':'date'},
))

time_field = forms.TimeField(
    required=True,
    label='Heure',
    widget=forms.TimeInput
        (attrs={'class':"form-control currentTime",
                'type':'time'},
))

def item_field():
    """ formated item field """
    return forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select
            (attrs={'class':"form-control hide"}),
        label='',
        )

def tomorrow_input(date, time, tz_offset):
    """ compare form input and timezone.now() with the same timezone"""
    current_tz = timezone.get_current_timezone()
    # get datetime_form and now() user in utc
    dt_form = datetime.datetime.combine(date, time, tzinfo=pytz.utc) + timedelta(minutes=tz_offset)
    user_now = timezone.now()
    # get both variable in current timezone in order to compare dates
    dt_form = current_tz.normalize(dt_form.astimezone(current_tz))
    user_now = current_tz.normalize(user_now.astimezone(current_tz))

    if dt_form.date() > user_now.date():
        return True
    return False
