#!/usr/bin/env python

"""
Module interacting with ConsoCig models
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from QuitSoonApp.models import Paquet, ConsoCig
from .manager import ManagerConso


class SmokeManager(ManagerConso):
    """Manage informations of cigarette consumption"""

    def __init__(self, user, data, tz_offset=0):
        ManagerConso.__init__(self, user, data)
        self.id_smoke = self.get_request_data('id_smoke')
        if not self.id_smoke:
            self.datetime_cig = self.get_datetime_client_aware(
                self.get_request_data('date_smoke'),
                self.get_request_data('time_smoke'),
                tz_offset
                )
            self.given = self.get_request_data('given_field')

    @property
    def get_conso_cig(self):
        """get ConsoCig instance with id or other data"""
        try:
            if self.id_smoke:
                smoke = ConsoCig.objects.get(id=self.id_smoke)
            else:
                smoke = ConsoCig.objects.get(
                    user=self.user,
                    datetime_cig=self.datetime_cig,
                    paquet=self.get_pack,
                    given=self.given,
                    )
            return smoke
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    @property
    def get_pack(self):
        """get Paquet instance with id or other data"""
        try:
            if self.id_smoke:
                # when user wants to delete a smoke, smoke id is returned in request
                return self.get_conso_cig.paquet
            if self.given :
                return None
            type_cig_field = self.get_request_data('type_cig_field')
            field = ''.join((type_cig_field.lower(), '_pack_field'))
            id_pack = self.get_request_data(field)
            return Paquet.objects.get(id=id_pack)
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    def create_conso_cig(self):
        """Create pack from data"""
        try:
            newconsocig = ConsoCig.objects.create(
                user=self.user,
                datetime_cig=self.datetime_cig,
                paquet=self.get_pack,
                given=self.given,
                )
            self.id_smoke = newconsocig.id
            return newconsocig
        except (IntegrityError, AttributeError):
            return None

    def delete_conso_cig(self):
        """delete ConsoCig instance with id"""
        try:
            if self.id_smoke:
                self.get_conso_cig.delete()
        except AttributeError:
            pass
