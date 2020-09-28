#!/usr/bin/env python
# pylint: disable=W0613 #Unused argument 'view_func', 'view_args', 'view_kwargs'

"""Url acces requirement (authentication and profile)"""


import re

from django.conf import settings
from django.shortcuts import redirect
from QuitSoonApp.models import UserProfile


EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]

EXEMPT_URLS_PROFILE = EXEMPT_URLS + [re.compile(settings.PROFILE_URL.lstrip('/'))]
if hasattr(settings, 'PROFILE_EXEMPT_URLS'):
    EXEMPT_URLS_PROFILE += [re.compile(url) for url in settings.PROFILE_EXEMPT_URLS]


class AccessRequirementMiddleware:
    """Url acces requirement middlexare (authentication and profile)"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        """process requirements called just before Django calls the view"""
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')

        if not request.user.is_authenticated:
            if not any(url.match(path) for url in EXEMPT_URLS):
                return redirect(settings.LOGIN_URL)
        else:
            if not UserProfile.objects.filter(user=request.user).exists():
                if not any(url.match(path) for url in EXEMPT_URLS_PROFILE):
                    return redirect(settings.PROFILE_URL)
