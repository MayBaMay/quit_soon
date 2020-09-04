from os import walk, remove
import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command

from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophy
)


class Command(BaseCommand):
    help = 'Exports user data with username in option'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        path = 'QuitSoonApp/dumps'
        f = []
        for (dirpath, dirnames, filenames) in walk(path):
            for filename in filenames:
                f.append("{}/{}".format(path, filename))

        for file in sorted(f):
            with open(file, encoding='utf-8') as data_file:
                call_command('loaddata', file, app_label='QuitSoonApp')
                remove(file)
