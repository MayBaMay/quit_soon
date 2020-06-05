#!/usr/bin/env python

"""
This module reset userprofile parameters and reset users informations related
such as informations in tables : ConsoCig, ConsoAlternative, Objectif and Trophee
"""
from django.contrib.auth.models import User
from ..models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)

class ResetProfile:

    def __init__(self, user, args):
        self.user = user
        self.datas = args
        self.date_start = self.get_request_data('date_start')
        self.starting_nb_cig = self.get_request_data('starting_nb_cig')
        self.ref_pack = self.get_request_data('ref_pack')
        self.clean_old_datas()

    def get_request_data(self, data):
        """get data from dict passed as argument"""
        try:
            return self.datas[data]
        except KeyError:
            return None

    def clean_old_datas(self):
        """Clean all datas concerned for stats features"""
        # DELETE DATAS
        UserProfile.objects.filter(user=self.user).delete()
        ConsoCig.objects.filter(user=self.user).delete()
        ConsoAlternative.objects.filter(user=self.user).delete()
        Objectif.objects.filter(user=self.user).delete()
        Trophee.objects.filter(user=self.user).delete()
        # CLEAN COLUMN FIRST, ALL FALSE
        Paquet.objects.filter(user=self.user, first=True).update(first=False)
        # CLEAN UNDISPLAYED PACKS & ALTERNATIVES
        Paquet.objects.filter(user=self.user, display=False).delete()
        Alternative.objects.filter(user=self.user, display=False).delete()
        
    def new_profile(self):
        """
        Create a new profile for user (old profile deleted in __init__)
        and update wich pack has first column == True (will be used to calculate user savings)
        """
        UserProfile.objects.create(
            user=self.user,
            date_start=self.date_start,
            starting_nb_cig=self.starting_nb_cig
        )
        Paquet.objects.filter(id=self.ref_pack).update(first=True)
