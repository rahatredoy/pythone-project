"""
Create the PostgreSQL schema "minishop" (run once, before migrate).

    python manage.py create_schema

settings.py uses  search_path=minishop  so all MiniShop tables live in this
schema, separate from any other tables in the same database.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create the "minishop" PostgreSQL schema if it does not exist'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('CREATE SCHEMA IF NOT EXISTS minishop')
        self.stdout.write(self.style.SUCCESS('Schema "minishop" is ready. Now run: python manage.py migrate'))
