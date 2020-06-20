from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class EmailAuthBackend(BaseBackend):
    """
    Email Authentication Backend
    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """
    def authenticate(self, request, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk = user_id)
            # Note that you MUST use pk = user_id in getting the user.
            # Otherwise, it will fail and even though the user is authenticated,
            # the user will not be logged in
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None
