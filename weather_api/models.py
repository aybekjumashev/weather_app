from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name="City")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Firstname")
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lastname")


class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    temp = models.FloatField()
    desc = models.CharField(max_length=200)
    humidity = models.IntegerField()
    speed = models.FloatField()
    current_time = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('city', 'latitude', 'longitude')
