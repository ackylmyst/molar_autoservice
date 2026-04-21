from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.CharField(max_length=100, unique=True)
    hash_passwd = models.TextField()
    
    class Meta:
        db_table = 'users'
        managed = False
    
    def set_password(self, raw_password):
        self.hash_passwd = make_password(raw_password)


class Client(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id', primary_key=True)
    phone = models.CharField(max_length=20)
    type_client_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'client'
        managed = False


class Car(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.IntegerField()
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    vin = models.CharField(max_length=50, null=True, blank=True)
    plate_number = models.CharField(max_length=20)
    year_produced = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'cars'
        managed = False
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    status_id = models.IntegerField(null=True, blank=True)
    payment_id = models.IntegerField(null=True, blank=True)
    problem_desc = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    car_id = models.IntegerField()  # NOT NULL, обязательное поле
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='client_id')
    
    class Meta:
        db_table = 'orders'
        managed = False
