#!/usr/bin/env python

"""
This module reset userprofile parameters and reset users informations related
such as informations in tables : ConsoCig, ConsoAlternative, Objectif and trophy
"""

from .manager import BaseManager
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophy
)


class ProfileManager(BaseManager):
    """Manage informations of Profile"""

    def __init__(self, user, data):
        BaseManager.__init__(self, user, data)
        self.date_start = self.get_request_data('date_start')
        self.starting_nb_cig = self.get_request_data('starting_nb_cig')
        self.ref_pack = self.get_request_data('ref_pack')
        self.clean_old_datas()

    def clean_old_datas(self):
        """Clean all data concerned for stats features"""
        # DELETE DATAS
        UserProfile.objects.filter(user=self.user).delete()
        ConsoCig.objects.filter(user=self.user).delete()
        ConsoAlternative.objects.filter(user=self.user).delete()
        Objectif.objects.filter(user=self.user).delete()
        Trophy.objects.filter(user=self.user).delete()
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
