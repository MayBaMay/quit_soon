import json

from django.core.serializers import serialize
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophy
)


class Command(BaseCommand):
    help = 'Exports user data with username in option'

    def add_arguments(self, parser):
        parser.add_argument('user_username', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['user_username']:
            try:
                user = User.objects.get(username=username)
                db_json = {
                    'QuitSoonApp/dumps/db0_User.json':User.objects.filter(username=username),
                    'QuitSoonApp/dumps/db1_UserProfile.json':UserProfile.objects.filter(user=user),
                    'QuitSoonApp/dumps/db2_Paquet.json':Paquet.objects.filter(user=user),
                    'QuitSoonApp/dumps/db3_ConsoCig.json':ConsoCig.objects.filter(user=user),
                    'QuitSoonApp/dumps/db4_Alternative.json': Alternative.objects.filter(user=user),
                    'QuitSoonApp/dumps/db5_ConsoAlternative.json':ConsoAlternative.objects.filter(user=user),
                    'QuitSoonApp/dumps/db6_Objectif.json':Objectif.objects.filter(user=user),
                    'QuitSoonApp/dumps/db7_Trophy.json':Trophy.objects.filter(user=user),
                    }
                for key, value in db_json.items():
                    with open(key, "w") as out:
                        serialize('json', value, stream=out)
            except User.DoesNotExist:
                raise CommandError('User "%s" does not exist' % username)
