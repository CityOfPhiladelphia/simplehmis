import csv
from django.core.management.base import BaseCommand, CommandError
from simplehmis.models import Project


class Command(BaseCommand):
    help = ('Loads projects from a CSV file. The file must have a column '
        'named "ProjectName".')

    def add_arguments(self, parser):
        parser.add_argument('projects_filename', nargs=1, type=str)

    def handle(self, *args, **options):
        projects_filename = options['projects_filename'][0]
        Project.objects.create_from_csv_file(projects_filename)
