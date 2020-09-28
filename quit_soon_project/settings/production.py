#!/usr/bin/env python
# pylint: disable=W0611 #Unused import * (unused-import)

"""
Production settings
"""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from dotenv import load_dotenv

from . import *

load_dotenv()

DEBUG = False

ALLOWED_HOSTS += ['134.209.202.228', '.nicotinekill.com']

sentry_sdk.init(
    dsn="https://a09a8f5116374a58a3ae749ffd89b36d@o371148.ingest.sentry.io/5353152",
    integrations=[DjangoIntegration()],
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = 'NicotineKill <noreply@nicotinekill.com>'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
