# ml/migrations/0002_create_partitioned_table.py
from django.db import migrations, connection
from datetime import datetime
def create_partitioned_table(apps, schema_editor):
    with connection.cursor() as cursor:
        # Drop the existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS core_appariel_data CASCADE;")

        # Create the new partitioned table
        cursor.execute("""
            CREATE TABLE core_appariel_data (
                id SERIAL,
                appariel_id INTEGER NOT NULL REFERENCES core_appariel(id),
                datetime TIMESTAMP NOT NULL,
                data JSONB,
                PRIMARY KEY (id, datetime) -- Include timestamp in the primary key
            ) PARTITION BY RANGE (datetime);
        """)
    start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2025-01-01', '%Y-%m-%d')
    current_date = start_date

    while current_date < end_date:
        partition_name = f"core_appariel_data_{current_date.strftime('%Y%m')}"

        # Calculate next month's first day
        next_month = current_date.month + 1 if current_date.month < 12 else 1
        next_year = current_date.year + 1 if next_month == 1 else current_date.year
        next_date = datetime(next_year, next_month, 1)

        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF core_appariel_data
                FOR VALUES FROM ('{current_date}') TO ('{next_date}');
            """)

        current_date = next_date

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_partitioned_table),
    ]
