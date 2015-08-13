from django.core.management.base import BaseCommand
from django.db import transaction
from simplehmis.models import Client


class Command(BaseCommand):
    help = ('Loads clients from a CSV file.')

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1, type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        with transaction.atomic():
            Client.objects.load_from_csv_file(filename)
