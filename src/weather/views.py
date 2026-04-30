from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import WeatherObservation, WeatherStats
from .serializers import WeatherObservationSerializer, WeatherStatsSerializer
from .filters import WeatherObservationFilter, WeatherStatsFilter


class WeatherObservationListView(generics.ListAPIView):
    serializer_class = WeatherObservationSerializer
    filterset_class = WeatherObservationFilter
    queryset = WeatherObservation.objects.select_related('station').order_by('date')

    @extend_schema(
        summary="List weather observations",
        description="Returns paginated weather observations. Filter by station_id and/or date.",
        parameters=[
            OpenApiParameter(name='station_id', type=str, description='Weather station ID'),
            OpenApiParameter(name='date', type=str, description='Date in YYYY-MM-DD format'),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class WeatherStatsListView(generics.ListAPIView):
    serializer_class = WeatherStatsSerializer
    filterset_class = WeatherStatsFilter
    queryset = WeatherStats.objects.select_related('station').order_by('year')

    @extend_schema(
        summary="List weather statistics",
        description="Returns paginated yearly weather statistics per station. Filter by station_id and/or year.",
        parameters=[
            OpenApiParameter(name='station_id', type=str, description='Weather station ID'),
            OpenApiParameter(name='year', type=int, description='Year as integer e.g. 1985'),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)