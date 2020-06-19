#!/usr/bin/env python

from dateutil import relativedelta
import datetime


def get_delta_last_event(last_time):
        delta = relativedelta.relativedelta(datetime.datetime.now(), last_time)
        deltas = {
            'month': ['mois', delta.months],
            'days': ['jours', delta.days],
            'hours':['heures', delta.hours],
            'minutes': ['minutes', delta.minutes],
            }
        last_event = []
        for key, value in deltas.items():
            if value[1]:
                last_event.append('{} {} '.format(value[1], value[0]))

        if last_event == []:
            last_event.append('0 minutes')
        return last_event
