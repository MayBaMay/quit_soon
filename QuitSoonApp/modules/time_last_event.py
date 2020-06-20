#!/usr/bin/env python

from dateutil import relativedelta
import datetime



def get_delta_last_event(last_time):
        delta = relativedelta.relativedelta(datetime.datetime.now(), last_time)
        deltas = {
            'year': [delta.years, 'an', 'ans'],
            'month': [delta.months, 'mois', 'mois'],
            'days': [delta.days, 'jour', 'jours'],
            'hours':[delta.hours, 'heure', 'heures'],
            'minutes': [delta.minutes, 'minute', 'minutes'],
            }
        last_event = []
        for key, value in deltas.items():
            if value[0]:
                if value[0] == 1:
                    last_event.append('{} {} '.format(value[0], value[1]))
                else:
                    last_event.append('{} {} '.format(value[0], value[2]))
        if last_event == []:
            last_event.append('0 minute ')
        return last_event
