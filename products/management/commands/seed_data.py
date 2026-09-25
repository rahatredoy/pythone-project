"""
Fill the database with sample categories and products.

    python manage.py seed_data

Data and images come from the sample_data/ folder. Running it again skips
categories/products that already exist (matched by name).
"""
import json

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from products.models import Category, Product

SAMPLE_DIR = settings.BASE_DIR / 'sample_data'
IMAGE_DIR = SAMPLE_DIR / 'images'


def attach_image(field, filename):
    """Copy an image from sample_data/images into media/ and link it to the field."""
    with open(IMAGE_DIR / filename, 'rb') as f:
        field.save(filename, File(f), save=False)


class Command(BaseCommand):
    help = 'Load sample categories and products into the database'

    def handle(self, *args, **options):
        data = json.loads((SAMPLE_DIR / 'products.json').read_text(encoding='utf-8'))

        # ---- categories ----
        categories = {}
        for item in data['categories']:
            category, created = Category.objects.get_or_create(name=item['name'])
            if created or not category.image:
                attach_image(category.image, item['image'])
                category.save()
            categories[item['name']] = category

        # ---- products ----
        created_count = 0
        for item in data['products']:
            if Product.objects.filter(name=item['name']).exists():
                continue

            images = item.pop('images')
            item['category'] = categories[item.pop('category')]
            product = Product(**item)

            # first image = main image, the rest go to image_2, image_3, image_4
            fields = [product.image, product.image_2, product.image_3, product.image_4]
            for field, filename in zip(fields, images):
                attach_image(field, filename)

            product.save()
            created_count += 1
            self.stdout.write(f'  + {product.name}')

        self.stdout.write(self.style.SUCCESS(
            f'Done: {len(categories)} categories, {created_count} new products.'
        ))
