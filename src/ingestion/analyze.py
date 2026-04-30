import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import transaction
from django.db.models import Avg, Sum
from django.db.models.functions import ExtractYear
from weather.models import WeatherObservation, WeatherStats

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)


def calculate_and_store_stats():
    logger.info("Starting stats calculation...")
    start_time = datetime.now()

    # Aggregate using ORM — AVG and SUM ignore NULLs natively
    stats = (
        WeatherObservation.objects
        .annotate(year=ExtractYear('date'))
        .values('station', 'year')
        .annotate(
            avg_max_temp=Avg('max_temp'),
            avg_min_temp=Avg('min_temp'),
            total_precipitation=Sum('precipitation'),
        )
        .order_by('station', 'year')
    )

    logger.info(f"Aggregation query complete — building stat objects...")

    stat_objects = [
        WeatherStats(
            station_id=row['station'],
            year=row['year'],
            avg_max_temp=row['avg_max_temp'],
            avg_min_temp=row['avg_min_temp'],
            total_precipitation=row['total_precipitation'],
        )
        for row in stats
    ]

    logger.info(f"Total stat rows to insert: {len(stat_objects)}")

    with transaction.atomic():
        # Idempotent — clear and recompute
        WeatherStats.objects.all().delete()

        WeatherStats.objects.bulk_create(
            stat_objects,
            batch_size=1000,
        )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info(f"Stats calculation complete.")
    logger.info(f"Total stat rows inserted: {len(stat_objects)}")
    logger.info(f"Duration: {duration:.2f} seconds")


if __name__ == '__main__':
    calculate_and_store_stats()