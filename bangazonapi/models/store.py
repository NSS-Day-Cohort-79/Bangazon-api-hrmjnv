from django.db import models
from django.contrib.auth.models import User
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE


class Store(SafeDeleteModel):

    _safedelete_policy = SOFT_DELETE_CASCADE
    seller = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=55)
    description = models.CharField(max_length=255)
