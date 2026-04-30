import pytest
from datetime import date
from weather.models import WeatherStation, WeatherObservation, WeatherStats
from ingestion.analyze import calculate_and_store_stats


@pytest.mark.django_db
class TestStatsCalculation:
    def setup_method(self):
        self.station = WeatherStation.objects.create(station_id='USC00110072')

    def test_avg_max_temp_correct(self):
        WeatherObservation.objects.create(
            station=self.station, date=date(1985, 1, 1),
            max_temp=10.0, min_temp=2.0, precipitation=0.5
        )
        WeatherObservation.objects.create(
            station=self.station, date=date(1985, 1, 2),
            max_temp=20.0, min_temp=4.0, precipitation=0.5
        )
        calculate_and_store_stats()
        stats = WeatherStats.objects.get(station=self.station, year=1985)
        assert stats.avg_max_temp == 15.0

    def test_nulls_ignored_in_avg(self):
        WeatherObservation.objects.create(
            station=self.station, date=date(1985, 1, 1),
            max_temp=10.0, min_temp=None, precipitation=None
        )
        calculate_and_store_stats()
        stats = WeatherStats.objects.get(station=self.station, year=1985)
        assert stats.avg_min_temp is None
        assert stats.total_precipitation is None

    def test_idempotent_rerun(self):
        WeatherObservation.objects.create(
            station=self.station, date=date(1985, 1, 1),
            max_temp=10.0, min_temp=2.0, precipitation=0.5
        )
        calculate_and_store_stats()
        calculate_and_store_stats()
        assert WeatherStats.objects.count() == 1