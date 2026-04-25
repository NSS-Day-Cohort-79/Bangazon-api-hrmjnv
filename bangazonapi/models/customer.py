from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):

    user = models.OneToOneField(User, on_delete=models.DO_NOTHING,)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=55)
    likes = models.ManyToManyField('Product', through='ProductLike', related_name="customer_likes")

    @property
    def recommended_by(self):
        return self.__recommends

    @recommended_by.setter
    def recommended_by(self, value):
        self.__recommends = value

    @property
    def recommendations(self):
        return self.__recommendations

    @recommendations.setter
    def recommendations(self, value):
        self.__recommendations = value