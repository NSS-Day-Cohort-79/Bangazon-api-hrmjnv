from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=55)
    description = models.CharField(max_length=255)
