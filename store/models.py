from django.db import models
from bridge.models import User
from django.core.validators import RegexValidator
import re
from django.utils.translation import gettext_lazy as _
from bridge.base.files import get_file_path
# Create your models here.

def get_store_photo_file_path(instance, filename):
    return get_file_path(instance, filename, "store/photo")

class Store(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField()
    phone_number = models.CharField(max_length=13,validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _(
            'Only numbers are allowed in format 000-000-000-000'), 'invalid')
    ])
    country = models.CharField(max_length=100)
    website = models.CharField(max_length=1020)
    facebook = models.CharField(max_length=1020)
    instagram = models.CharField(max_length=1020)
    twitter = models.CharField(max_length=1020)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)



class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE,)
    name = models.CharField(max_length=150)
    price = models.FloatField()
    stock = models.IntegerField()
    description = models.TextField()
    category = models.CharField(max_length=150)
    photos = models.ImageField(upload_to=get_store_photo_file_path)


class Service(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE,)
    name = models.CharField(max_length=150)
    price = models.FloatField()
    # stock = models.IntegerField()
    description = models.TextField()
    category = models.CharField(max_length=150)
    photos = models.ImageField(upload_to=get_store_photo_file_path)
