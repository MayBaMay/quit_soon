from . import *

DEBUG = False


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'maylis.baschet@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'NicotineKill <noreply@nicotinekill.com>'
