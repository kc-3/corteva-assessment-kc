
from django.contrib import admin
from .models import WeatherStation, WeatherObservation, WeatherStats

@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ['station_id']
    search_fields = ['station_id']

@admin.register(WeatherObservation)
class WeatherObservationAdmin(admin.ModelAdmin):
    list_display = ['station', 'date', 'max_temp', 'min_temp', 'precipitation']
    list_filter = ['station']
    search_fields = ['station__station_id']

@admin.register(WeatherStats)
class WeatherStatsAdmin(admin.ModelAdmin):
    list_display = ['station', 'year', 'avg_max_temp', 'avg_min_temp', 'total_precipitation']
    list_filter = ['year']
    