import pytest
from rest_framework.test import APIClient
from weather.models import WeatherStation, WeatherObservation, WeatherStats
from datetime import date


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def station(db):
    return WeatherStation.objects.create(station_id='USC00110072')


@pytest.fixture
def observations(station):
    WeatherObservation.objects.create(
        station=station, date=date(1985, 1, 1),
        max_temp=10.5, min_temp=2.3, precipitation=0.5
    )
    WeatherObservation.objects.create(
        station=station, date=date(1985, 1, 2),
        max_temp=11.0, min_temp=3.0, precipitation=None
    )
    WeatherObservation.objects.create(
        station=station, date=date(1986, 1, 1),
        max_temp=9.0, min_temp=1.0, precipitation=1.0
    )


@pytest.fixture
def stats(station):
    WeatherStats.objects.create(
        station=station, year=1985,
        avg_max_temp=10.75, avg_min_temp=2.65, total_precipitation=0.5
    )
    WeatherStats.objects.create(
        station=station, year=1986,
        avg_max_temp=9.0, avg_min_temp=1.0, total_precipitation=1.0
    )


@pytest.mark.django_db
class TestWeatherObservationAPI:
    def test_list_returns_200(self, api_client, observations):
        response = api_client.get('/api/weather/')
        assert response.status_code == 200

    def test_filter_by_station_id(self, api_client, observations):
        response = api_client.get('/api/weather/?station_id=USC00110072')
        assert response.data['count'] == 3

    def test_filter_by_date(self, api_client, observations):
        response = api_client.get('/api/weather/?date=1985-01-01')
        assert response.data['count'] == 1

    def test_pagination_structure(self, api_client, observations):
        response = api_client.get('/api/weather/')
        assert all(k in response.data for k in ['count', 'next', 'previous', 'results'])

    def test_null_values_in_response(self, api_client, observations):
        response = api_client.get('/api/weather/?date=1985-01-02')
        assert response.data['results'][0]['precipitation'] is None


@pytest.mark.django_db
class TestWeatherStatsAPI:
    def test_list_returns_200(self, api_client, stats):
        response = api_client.get('/api/weather/stats/')
        assert response.status_code == 200

    def test_filter_by_year(self, api_client, stats):
        response = api_client.get('/api/weather/stats/?year=1985')
        assert response.data['count'] == 1

    def test_filter_by_invalid_year(self, api_client, stats):
        response = api_client.get('/api/weather/stats/?year=9999')
        assert response.data['count'] == 0