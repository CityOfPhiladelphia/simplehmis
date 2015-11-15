from django.core.management.base import BaseCommand
from django.db import transaction
from simplehmis.models import Client


class Command(BaseCommand):
    help = ('Loads clients from a CSV file.')

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('-s', '--strong-matching', action='store_true')
        parser.add_argument('-i', '--interactive', action='store_true')

    def handle(self, *args, **options):
        filename = options['filename']
        strong_matching = options['strong_matching']
        interactive = options['interactive']

        if filename == '-':
            from sys import stdin
            Client.objects.load_from_csv_stream(stdin, interactive=interactive, strong_matching=strong_matching)
        else:
            Client.objects.load_from_csv_file(filename, interactive=interactive, strong_matching=strong_matching)
