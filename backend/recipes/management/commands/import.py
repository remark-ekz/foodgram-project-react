import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredients

MYPATH = './'
FILENAME = 'ingredients.csv'


class Command(BaseCommand):
    help = 'Load csv'

    def handle(self, *args, **options):
        with open(MYPATH + '/' + FILENAME, encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(
                csv_file,
                fieldnames=['name', 'measure_unit'],
                delimiter=',')
            for string in csv_reader:
                ingredients = Ingredients(
                    name=string['name'],
                    measure_unit=string['measure_unit']
                    )
                ingredients.save()
            print('Загрузка завершена')
