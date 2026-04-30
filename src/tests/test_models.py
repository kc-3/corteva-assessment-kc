import pytest
from django.db.utils import IntegrityError
from weather.models import WeatherStation, WeatherObservation, WeatherStats
from datetime import date


@pytest.mark.django_db
class TestWeatherStation:
    def test_create_station(self):
        station = WeatherStation.objects.create(station_id='USC00110072')
        assert station.station_id == 'USC00110072'

    def test_station_id_unique(self):
        WeatherStation.objects.create(station_id='USC00110072')
        with pytest.raises(IntegrityError):
            WeatherStation.objects.create(station_id='USC00110072')


@pytest.mark.django_db
class TestWeatherObservation:
    def setup_method(self):
        self.station = WeatherStation.objects.create(station_id='USC00110072')

    def test_null_values_allowed(self):
        obs = WeatherObservation.objects.create(
            station=self.station, date=date(1985, 1, 1),
            max_temp=None, min_temp=None, precipitation=None,
        )
        assert obs.max_temp is None

    def test_duplicate_station_date_raises(self):
        WeatherObservation.objects.create(
            station=self.station, date=date(1985, 1, 1), max_temp=10.5,
        )
        with pytest.raises(IntegrityError):
            WeatherObservation.objects.create(
                station=self.station, date=date(1985, 1, 1), max_temp=9.0,
            )


@pytest.mark.django_db
class TestWeatherStats:
    def setup_method(self):
        self.station = WeatherStation.objects.create(station_id='USC00110072')

    def test_duplicate_station_year_raises(self):
        WeatherStats.objects.create(station=self.station, year=1985)
        with pytest.raises(IntegrityError):
            WeatherStats.objects.create(station=self.station, year=1985)

    def test_null_stats_allowed(self):
        stats = WeatherStats.objects.create(
            station=self.station, year=1990,
            avg_max_temp=None, avg_min_temp=None, total_precipitation=None,
        )
        assert stats.avg_max_temp is None