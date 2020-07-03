from . import *

from dotenv import load_dotenv


load_dotenv()


DEBUG = False
DOMAIN = "http://nicotinekill.com"

EMAIL_HOST = 'mail.gandi.net'
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'NicotineKill <noreply@nicotinekill.com>'
