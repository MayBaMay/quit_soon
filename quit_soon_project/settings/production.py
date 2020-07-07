from . import *

from dotenv import load_dotenv


load_dotenv()

DEBUG = False

ALLOWED_HOSTS += ['134.209.202.228', 'www.nicotinekill.com']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = 'NicotineKill <noreply@nicotinekill.com>'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
