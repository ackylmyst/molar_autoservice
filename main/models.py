from django.db import models

class Request(models.Model):
    phone = models.CharField(max_length=20)
    car_model = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.id} - {self.car_model}"
