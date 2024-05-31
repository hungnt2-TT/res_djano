from django.db import models
from geoposition.fields import GeopositionField
from django.contrib.auth.models import User


# Create your models here.
class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    position = GeopositionField()
    phone_number = models.CharField(max_length=15)
    description = models.TextField()

    def __str__(self):
        return self.name