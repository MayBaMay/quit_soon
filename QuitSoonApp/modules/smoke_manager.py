#!/usr/bin/env python

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from QuitSoonApp.models import Paquet, ConsoCig


class SmokeManager:
    """Manage informations of cigarette consumption"""

    def __init__(self, user, datas):
        self.datas = datas
        self.user = user
        self.id = self.get_request_data('id_smoke')
        self.date_cig = self.get_request_data('date_smoke')
        self.time_cig = self.get_request_data('time_smoke')
        self.given = self.get_request_data('given_field')
        self.paquet = self.get_pack

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
                    paquet=self.paquet,
                    given=self.given,
                    )
            return smoke
        except (ObjectDoesNotExist, ValueError, AttributeError):
            return None

    @property
    def get_pack(self):
        try:
            # when user wants to delete a smoke, smoke id is returned in request
            return self.get_conso_cig.paquet
        except (ObjectDoesNotExist, AttributeError):
            if self.given :
                return None
            else:
                # check type_cig selected to keep datas from the appropriated field
                if self.get_request_data('type_cig_field') == 'IND':
                    try:
                        return Paquet.objects.get(id = int(self.get_request_data('indus_pack_field')))
                    except (ObjectDoesNotExist, ValueError):
                        pass
                elif self.get_request_data('type_cig_field') == 'ROL':
                    try:
                        return Paquet.objects.get(id = int(self.get_request_data('rol_pack_field')))
                    except (ObjectDoesNotExist, ValueError):
                        pass
                elif self.get_request_data('type_cig_field') == 'CIGARES':
                    try:
                        return Paquet.objects.get(id = int(self.get_request_data('cigares_pack_field')))
                    except (ObjectDoesNotExist, ValueError):
                        pass
                elif self.get_request_data('type_cig_field') == 'PIPE':
                    try:
                        return Paquet.objects.get(id = int(self.get_request_data('pipe_pack_field')))
                    except (ObjectDoesNotExist, ValueError):
                        pass
                elif self.get_request_data('type_cig_field') == 'NB':
                    try:
                        return Paquet.objects.get(id = int(self.get_request_data('nb_pack_field')))
                    except (ObjectDoesNotExist, ValueError):
                        pass
                elif self.get_request_data('type_cig_field') == 'GR':
                    try:
                        return Paquet.objects.get(id = int(self.get_request_data('gr_pack_field')))
                    except (ObjectDoesNotExist, ValueError):
                        pass
            return None

    def create_conso_cig(self):
        """Create pack from datas"""
        try:
            newconsocig = ConsoCig.objects.create(
                user=self.user,
                date_cig=self.date_cig,
                time_cig=self.time_cig,
                paquet=self.paquet,
                given=self.given,
                )
            self.id = newconsocig.id
            return newconsocig
        except IntegrityError:
            return None

    def delete_conso_cig(self):
        # only delete ConsoCig if request gives id with delete_smoke view
        if self.id:
            self.get_conso_cig.delete()
