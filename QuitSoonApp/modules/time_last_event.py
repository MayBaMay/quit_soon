#!/usr/bin/env python

"""
Module calculate delta between now and last event
and return it into formated string
"""

from dateutil import relativedelta
from django.utils import timezone


def get_delta_last_event(last_time):
    """
    function calculate delta between now and last event
    and return it into formated string
    """
    delta = relativedelta.relativedelta(timezone.now(), last_time)
    deltas = {
        'year': [delta.years, 'an', 'ans'],
        'month': [delta.months, 'mois', 'mois'],
        'days': [delta.days, 'jour', 'jours'],
        'hours':[delta.hours, 'heure', 'heures'],
        'minutes': [delta.minutes, 'minute', 'minutes'],
        }
    last_event = []
    for value in deltas.values():
        if value[0]:
            if value[0] == 1:
                last_event.append('{} {} '.format(value[0], value[1]))
            else:
                last_event.append('{} {} '.format(value[0], value[2]))
    if last_event == []:
        last_event.append('0 minute ')
    return last_event
