#!/usr/bin/env python

"""
This module reset userprofile parameters and reset users informations related
such as informations in tables : ConsoCig, ConsoAlternative, Objectif and Trophee
"""
from django.contrib.auth.models import User
from ..models import (
    UserProfile,
    ConsoCig,
    ConsoAlternative,
    Objectif, Trophee
)

class ResetProfile:

    def __init__(self, user, parameters):
        self.user = user
        self.date_start = parameters['date_start']
        self.starting_nb_cig = parameters['starting_nb_cig']
        self.clean_old_datas()

    def clean_old_datas(self):
        UserProfile.objects.filter(user=self.user).delete()
        ConsoCig.objects.filter(user=self.user).delete()
        ConsoAlternative.objects.filter(user=self.user).delete()
        Objectif.objects.filter(user=self.user).delete()
        Trophee.objects.filter(user=self.user).delete()

    def new_profile(self):
        userprofile = UserProfile.objects.create(
            user=self.user,
            date_start=self.date_start,
            starting_nb_cig=self.starting_nb_cig
        )
        return userprofile
