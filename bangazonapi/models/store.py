from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):

    seller = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=55)
    description = models.CharField(max_length=255)
