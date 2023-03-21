from django.db import models
from bridge.models import User
from django.core.validators import RegexValidator
import re
from django.utils.translation import gettext_lazy as _
from bridge.base.files import get_file_path
from django.core.validators import FileExtensionValidator

# Create your models here.

def get_store_photo_file_path(instance, filename):
    return get_file_path(instance, filename, "store/photo")

def get_store_video_file_path(instance, filename):
    return get_file_path(instance, filename, "store/video")

def get_store_photo_deck_path(instance, filename):
    return get_file_path(instance, filename, "store/deck")

def get_store_document_file_path(instance, filename):
    return get_file_path(instance, filename, "store/document")




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



class PitchingDeck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_file = models.FileField(upload_to=get_store_video_file_path)
    deck = models.FileField(upload_to=get_store_photo_deck_path)



class Comment(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    pitching_deck = models.ForeignKey(PitchingDeck, on_delete=models.CASCADE)
    comment = models.TextField()
    photo = models.ImageField(upload_to=get_store_photo_file_path, null=True, blank=True)
    video = models.FileField(upload_to=get_store_video_file_path, null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi', 'mp4', 'webm', 'mkv'])])
    document = models.FileField(upload_to=get_store_document_file_path, null=True)

    def __str__(self):
        return self.comment
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        #compress_img(self.photo)

