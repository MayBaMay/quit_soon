#!/usr/bin/env python

from django.test import TransactionTestCase, TestCase
from django.utils.timezone import make_aware
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)
