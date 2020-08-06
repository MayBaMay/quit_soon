#!/usr/bin/env python

import datetime
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from QuitSoonApp.models import Paquet, ConsoCig


class SmokeManager:
    """Manage informations of cigarette consumption"""

    def __init__(self, user, datas, tz_offset=0):
        self.datas = datas
        self.user = user
        self.id = self.get_request_data('id_smoke')
        if not self.id:
            self.date_cig, self.time_cig = self.get_date_time_cig_aware(
                self.get_request_data('date_smoke'),
                self.get_request_data('time_smoke'),
                tz_offset
                )
            print(self.date_cig, self.time_cig)
            self.given = self.get_request_data('given_field')

    def get_date_time_cig_aware(self, date_smoke, time_smoke, tz_offset):
        try:
            dt_smoke = datetime.datetime.combine(date_smoke, time_smoke)
            dt_smoke -= timedelta(hours=tz_offset)
            date_cig = dt_smoke.date()
            time_cig = dt_smoke.time()
            return date_cig, time_cig
        except TypeError:
            # get_request_data returned None
            return None, None

    def get_request_data(self, data):
        try:
            return self.datas[data]
        except KeyError:
            return None

    @property
    def get_conso_cig(self):
        try:
            if self.id:
                smoke = ConsoCig.objects.get(id=self.id)
            else:
                smoke = ConsoCig.objects.get(
                    user=self.user,
                    date_cig=self.date_cig,
                    time_cig=self.time_cig,
                    paquet=self.get_pack,
                    given=self.given,
                    )
            return smoke
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    @property
    def get_pack(self):
        try:
            if self.id:
                # when user wants to delete a smoke, smoke id is returned in request
                return self.get_conso_cig.paquet
            else:
                if self.given :
                    return None
                else:
                    type = self.get_request_data('type_cig_field')
                    field = ''.join((type.lower(), '_pack_field'))
                    id_pack = self.get_request_data(field)
                    return Paquet.objects.get(id=id_pack)
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    def create_conso_cig(self):
        """Create pack from datas"""
        try:
            newconsocig = ConsoCig.objects.create(
                user=self.user,
                date_cig=self.date_cig,
                time_cig=self.time_cig,
                paquet=self.get_pack,
                given=self.given,
                )
            self.id = newconsocig.id
            return newconsocig
        except (IntegrityError, AttributeError) as e:
            print(e)
            return None

    def delete_conso_cig(self):
        try:
            if self.id:
                self.get_conso_cig.delete()
        except AttributeError:
            pass
