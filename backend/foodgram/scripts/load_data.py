import csv
import os

from recipes.models import Ingredient

PROJECT_DIR = os.path.dirname(os.path.dirname(os.getcwd()))


def run():
    with open(f'{PROJECT_DIR}/data/ingredients.csv') as file:
        reader = csv.reader(file)

        for row in reader:
            _, ingredient = Ingredient.objects.get_or_create(
                name=row[0],
                measurement_unit=row[1]
            )


if __name__ == "__main__":
    run()


with open(f'{PROJECT_DIR}/data/ingredients.csv') as file:
        reader = csv.reader(file)
        for row in reader:
             print(row)
             break