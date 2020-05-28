#!/usr/bin/env python

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from QuitSoonApp.models import Alternative, ConsoAlternative


class HealthManager:
    """Manage informations of healthy actions"""

    def __init__(self, user, datas):
        self.datas = datas
        self.user = user
        self.id = self.get_request_data('id_health')
    #     if not self.id:
    #         self.date_alter = self.get_request_data('date_health')
    #         self.time_alter = self.get_request_data('time_health')
    #         # self.alternative =
    #         # self.type_alternative_field = self.get_request_data('type_alternative_field')
    #         # self.sp_field = self.get_request_data('sp_field')
    #         # self.so_field = self.get_request_data('so_field')
    #         # self.lo_field = self.get_request_data('lo_field')
    #         # self.su_field = self.get_request_data('su_field')
    #     # self.alternative = self.get_alternative
    #
    # def get_request_data(self, data):
    #     try:
    #         return self.datas[data]
    #     except KeyError:
    #         return None
    #
    # @property
    # def get_conso_alternative(self):
    #     try:
    #         if self.id:
    #             health = ConsoAlternative.objects.get(id=self.id)
    #         else:
    #             health = ConsoAlternative.objects.get(
    #                 user=self.user,
    #                 date_alter=self.date_alter,
    #                 time_alter=self.time_alter,
    #                 alternative='',
    #                 duration='',
    #                 )
    #         return health
    #     except (ObjectDoesNotExist, ValueError, AttributeError):
    #         return None
    #
    # @property
    # def get_alternative(self):
    #     try:
    #         # when user wants to delete a smoke, smoke id is returned in request
    #         return self.get_conso_alternative.alternative
    #     except (ObjectDoesNotExist, AttributeError):
    #         if self.get_request_data('type_alternative_field') == 'Ac':
