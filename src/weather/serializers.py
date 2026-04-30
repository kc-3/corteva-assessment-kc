from rest_framework import serializers
from .models import WeatherObservation, WeatherStats


class WeatherObservationSerializer(serializers.ModelSerializer):
    station_id = serializers.CharField(source='station.station_id')

    class Meta:
        model = WeatherObservation
        fields = ['id', 'station_id', 'date', 'max_temp', 'min_temp', 'precipitation']


class WeatherStatsSerializer(serializers.ModelSerializer):
    station_id = serializers.CharField(source='station.station_id')

    class Meta:
        model = WeatherStats
        fields = ['id', 'station_id', 'year', 'avg_max_temp', 'avg_min_temp', 'total_precipitation']