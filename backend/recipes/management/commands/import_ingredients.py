from csv import reader
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('recipes/data/ingredients.csv', 'r', newline='') as csvfile:
            data = [
                Ingredient(name=name, measurement_unit=measurement_unit)
                for name, measurement_unit in reader(csvfile)
            ]
        Ingredient.objects.bulk_create(data)
