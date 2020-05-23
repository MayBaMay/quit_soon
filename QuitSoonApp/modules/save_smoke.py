#!/usr/bin/env python

from django import forms

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)


class SaveSmoke:
    """Save informations of cigarette consumtion"""

    def __init__(self, user, datas):
        self.user = user
        self.date_smoke = datas['date_smoke']
        self.time_smoke = datas['time_smoke']
        self.type_cig = datas['type_cig_field']
        self.pack = self.get_pack(datas)
        print(self.pack)

    def get_pack(self, datas):
        if self.type_cig == 'IND':
            try:
                return Paquet.objects.get(id = int(datas[('indus_pack_field')]))
            except (ObjectDoesNotExist, ValueError):
                pass
        elif self.type_cig == 'ROL':
            try:
                return Paquet.objects.get(id = int(datas[('rol_pack_field')]))
            except (ObjectDoesNotExist, ValueError):
                None
        elif self.type_cig == 'CIGARES':
            try:
                return Paquet.objects.get(id = int(datas[('cigares_pack_field')]))
            except (ObjectDoesNotExist, ValueError):
                None
        elif self.type_cig == 'PIPE':
            try:
                return Paquet.objects.get(id = int(datas[('pipe_pack_field')]))
            except (ObjectDoesNotExist, ValueError):
                None
        elif self.type_cig == 'NB':
            try:
                return Paquet.objects.get(id = int(datas[('nb_pack_field')]))
            except (ObjectDoesNotExist, ValueError):
                None
        elif self.type_cig == 'GR':
            try:
                return Paquet.objects.get(id = int(datas[('gr_pack_field')]))
            except (ObjectDoesNotExist, ValueError):
                None
