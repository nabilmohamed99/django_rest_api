# ml/management/commands/create_partitions.py
from django.core.management.base import BaseCommand
from django.db import connection
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Create partitions for the appariel_data table'

    def handle(self, *args, **options):
        start_date = date(2024, 1, 1)
        end_date = date(2025, 1, 1)
        current_date = start_date.replace(day=1)

        while current_date < end_date:
            partition_name = f"appariel_data_{current_date.strftime('%Y%m')}"

            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year + 1 if next_month == 1 else current_date.year
            next_date = current_date.replace(year=next_year, month=next_month)

            with connection.cursor() as cursor:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF appariel_data
                    FOR VALUES FROM ('{current_date.strftime('%Y-%m-%d')}') TO ('{next_date.strftime('%Y-%m-%d')}');
                """)
                self.stdout.write(f"Partition {partition_name} created.")

            current_date = next_date
