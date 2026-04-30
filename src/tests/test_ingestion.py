import pytest
import tempfile
import os
from datetime import date
from weather.models import WeatherStation, WeatherObservation
from ingestion.ingest import parse_line, ingest_file


class TestParseLine:
    def test_valid_line(self):
        result = parse_line('19850101\t100\t-50\t200')
        assert result['date'] == date(1985, 1, 1)
        assert result['max_temp'] == 10.0
        assert result['min_temp'] == -5.0
        assert result['precipitation'] == 2.0

    def test_missing_values_return_none(self):
        result = parse_line('19850101\t-9999\t-9999\t-9999')
        assert result['max_temp'] is None
        assert result['min_temp'] is None
        assert result['precipitation'] is None

    def test_malformed_line_returns_none(self):
        result = parse_line('bad_data')
        assert result is None


@pytest.mark.django_db
class TestIngestFile:
    def test_ingest_creates_records(self):
        station = WeatherStation.objects.create(station_id='TEST001')
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('19850101\t100\t-50\t200\n')
            f.write('19850102\t110\t-40\t0\n')
            tmpfile = f.name
        count = ingest_file(tmpfile, station)
        assert count == 2
        os.unlink(tmpfile)

    def test_ingest_dedup(self):
        station = WeatherStation.objects.create(station_id='TEST002')
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('19850101\t100\t-50\t200\n')
            tmpfile = f.name
        ingest_file(tmpfile, station)
        ingest_file(tmpfile, station)
        assert WeatherObservation.objects.filter(station=station).count() == 1
        os.unlink(tmpfile)