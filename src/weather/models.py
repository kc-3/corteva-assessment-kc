from django.db import models


class WeatherStation(models.Model):
    station_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.station_id

    class Meta:
        db_table = 'weather_station'


class WeatherObservation(models.Model):
    station = models.ForeignKey(
        WeatherStation,
        on_delete=models.CASCADE,
        related_name='observations'
    )
    date = models.DateField()
    max_temp = models.FloatField(null=True)
    min_temp = models.FloatField(null=True)
    precipitation = models.FloatField(null=True)

    class Meta:
        db_table = 'weather_observation'
        unique_together = ('station', 'date')
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['station', 'date']),
        ]

    def __str__(self):
        return f"{self.station.station_id} - {self.date}"


class WeatherStats(models.Model):
    station = models.ForeignKey(
        WeatherStation,
        on_delete=models.CASCADE,
        related_name='stats'
    )
    year = models.IntegerField()
    avg_max_temp = models.FloatField(null=True)
    avg_min_temp = models.FloatField(null=True)
    total_precipitation = models.FloatField(null=True)

    class Meta:
        db_table = 'weather_stats'
        unique_together = ('station', 'year')
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['station', 'year']),
        ]

    def __str__(self):
        return f"{self.station.station_id} - {self.year}"