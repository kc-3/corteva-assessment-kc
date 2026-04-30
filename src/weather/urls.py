from django.urls import path
from .views import WeatherObservationListView, WeatherStatsListView

urlpatterns = [
    path('weather/', WeatherObservationListView.as_view(), name='weather-list'),
    path('weather/stats/', WeatherStatsListView.as_view(), name='weather-stats-list'),
]