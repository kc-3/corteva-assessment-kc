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

from weather.models import WeatherStation, WeatherObservation
from django.db import transaction, connection

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)


def parse_line(line):
    """Parse a single line from a wx_data file. Returns dict or None."""
    fields = line.strip().split('\t')
    if len(fields) != 4:
        return None

    date_str, raw_max, raw_min, raw_precip = fields

    def to_celsius(val):
        v = int(val)
        return None if v == -9999 else round(v / 10.0, 2)

    def to_cm(val):
        v = int(val)
        return None if v == -9999 else round(v / 100.0, 2)

    return {
        'date': datetime.strptime(date_str.strip(), '%Y%m%d').date(),
        'max_temp': to_celsius(raw_max),
        'min_temp': to_celsius(raw_min),
        'precipitation': to_cm(raw_precip),
    }


def ingest_file(filepath, station):
    records = []
    with open(filepath, 'r') as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                records.append(
                    WeatherObservation(
                        station=station,
                        date=parsed['date'],
                        max_temp=parsed['max_temp'],
                        min_temp=parsed['min_temp'],
                        precipitation=parsed['precipitation'],
                    )
                )
    created = WeatherObservation.objects.bulk_create(
        records,
        batch_size=5000,
        ignore_conflicts=True
    )
    return len(created)


def run(data_dir):
    logger.info(f"Starting ingestion from: {data_dir}")
    start_time = datetime.now()
    total_ingested = 0
    files = list(Path(data_dir).glob('*.txt'))
    logger.info(f"Found {len(files)} station files")

    with transaction.atomic():
        for filepath in files:
            station_id = filepath.stem
            station, _ = WeatherStation.objects.get_or_create(station_id=station_id)
            count = ingest_file(filepath, station)
            total_ingested += count
            logger.info(f"{station_id}: {count} records ingested")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Total records ingested: {total_ingested}")
    logger.info(f"Duration: {duration:.2f} seconds")

if __name__ == '__main__':
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'wx_data'
    run(data_dir)