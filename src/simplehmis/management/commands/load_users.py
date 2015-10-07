import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from simplehmis.models import Project

User = get_user_model()


class Command(BaseCommand):
    help = ('Loads users from a CSV file.')

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1, type=str)
        parser.add_argument('--no-duplicates', dest='duplicates', action='store_false')

    def load_users_from_stream(self, usersfile, **options):
        reader = csv.DictReader(usersfile)
        with transaction.atomic():
            for row in reader:
                project_name = row.pop('project')
                staff_groups = row.pop('groups').split(',')

                row['is_staff'] = (row['is_staff'].lower() == 'true')
                row['is_active'] = (row['is_active'].lower() == 'true')
                row['is_superuser'] = (row['is_superuser'].lower() == 'true')

                if options['duplicates']:
                    user, _ = User.objects.get_or_create(
                        username=row['username'],
                        defaults=row)
                else:
                    user = User.objects.create(**row)

                if project_name:
                    project = Project.objects.get(name=project_name)
                    user.projects.add(project)

                groups = Group.objects.filter(name__in=staff_groups)
                user.groups.add(*groups)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        if filename == '-':
            from sys import stdin
            self.load_users_from_stream(stdin, **options)
        else:
            with open(filename, 'rU') as usersfile:
                self.load_users_from_stream(usersfile, **options)
