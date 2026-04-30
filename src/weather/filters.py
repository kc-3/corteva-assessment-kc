import django_filters
from .models import WeatherObservation, WeatherStats


class WeatherObservationFilter(django_filters.FilterSet):
    station_id = django_filters.CharFilter(
        field_name='station__station_id',
        lookup_expr='exact'
    )
    date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='exact'
    )

    class Meta:
        model = WeatherObservation
        fields = ['station_id', 'date']


class WeatherStatsFilter(django_filters.FilterSet):
    station_id = django_filters.CharFilter(
        field_name='station__station_id',
        lookup_expr='exact'
    )
    year = django_filters.NumberFilter(
        field_name='year',
        lookup_expr='exact'
    )

    class Meta:
        model = WeatherStats
        fields = ['station_id', 'year']