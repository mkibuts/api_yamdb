import csv

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import from .csv file to .sqlite3'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV file to import')
        parser.add_argument('model', type=str, help='Model for import')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        model_name = options['model']
        model = apps.get_model(app_label='reviews', model_name=model_name)
        with open(csv_file) as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    model_instance = model(*row)
                    model_instance.save()
                except ValueError:
                    pass
