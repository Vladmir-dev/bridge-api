from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
import uuid
from django_countries.fields import CountryField
from django.utils import timezone
import re
from django.utils.translation import gettext_lazy as _
import rstr
import os
from PIL import Image
from bridge.base.files import get_file_path
from rest_framework.authtoken.models import Token
from django.conf import settings
import jwt
from datetime import datetime, timedelta
from django.core.validators import FileExtensionValidator
# from django.db.models.signals import post_save
# Create your models here.


def get_wallet_account_number():
    return rstr.xeger(r'[A-Z]\d\d[A-Z][A-Z]\d')


def get_user_photo_file_path(instance, filename):
    return get_file_path(instance, filename, "user/photo")



# class Token(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auth_token'
#     )
#     key = models.CharField(max_length=40, unique=True)
#     created_at = models.DateTimeField(default=timezone.now)

#     def save(self, *args, **kwargs):
#         if not self.key:
#             self.key = Token.generate_key()
#         return super(Token, self).save(*args, **kwargs)


class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be set")
        
        if not email:
            raise ValueError("Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username=username, email=email, password=password, **extra_fields)
    
    


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.CharField(max_length=100, editable=False,
                            null=False, blank=False, unique=True, default=uuid.uuid4)
    username = models.CharField(
        max_length=150, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(
        max_length=255, blank=True, null=True, unique=True,)
    phone_number = models.CharField(max_length=13, validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _(
            'Only numbers are allowed in format 000-000-000-000'), 'invalid')
    ], blank=True, null=True, unique=True)
    sex = models.CharField(max_length=30, blank=True, default="", choices=(
        ('Male', 'Male'), ('Female', 'Female'), ('Other', 'other')))
    date_joined = models.DateTimeField(default=timezone.now)
    accepted_terms = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    country = CountryField(blank=True)
    nationality = CountryField(blank=True)
    city = models.CharField(max_length=200, blank=True)
    token = models.CharField(max_length=550, null=True, blank=True)
    photo = models.ImageField(
        upload_to=get_user_photo_file_path, null=True, blank=True)
    background_photo = models.ImageField(
        upload_to=get_user_photo_file_path, null=True, blank=True)
    anonymous = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self.generate_token()


    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        SIZE = (300, 300)

        if self.photo:
            img = Image.open(self.photo.path)
            img.thumbnail(SIZE)
            img.save(self.photo.path)

        # for field_name in ['photo', 'background_photo']:
        #     field = getattr(User, field_name)
        #     if field:
        #         img = Image.open(field)
        #         img.thumbnail(SIZE)
        #         img.save(self.field_name.path)

    def generate_token(self):
        dt = datetime.now() + timedelta(days=60)
        
        payload = {
            'id':self.pk,
            'exp':int(dt.strftime('%s'))
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        print("token======>", token)
        
        return token



class ChatMessage(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipient")
    message = models.TextField()
    photo = models.ImageField(upload_to=get_user_photo_file_path, null=True, blank=True)
    video = models.FileField(upload_to='videos', null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi', 'mp4', 'webm', 'mkv'])])
    document = models.FileField(upload_to='documents', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


# # add image field
class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    photo = models.ImageField(upload_to=get_user_photo_file_path, null=True, blank=True)
    video = models.FileField(upload_to='videos', null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi', 'mp4', 'webm', 'mkv'])])
    document = models.FileField(upload_to='documents', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{0} : {1}".format(self.user, self.message)


class RelationShip(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed")


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    wallet_no = models.CharField(_('Account Number'), max_length=10, unique=True, default=get_wallet_account_number, validators=[
                                 RegexValidator(re.compile(r'[A-Z]\d\d[A-Z][A-Z]\d'))])
    total_sent = models.FloatField(default=0)
    total_received = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wallet_no


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    comment = models.TextField()
    photo = models.ImageField(upload_to=get_user_photo_file_path, null=True, blank=True)
    video = models.FileField(upload_to='videos', null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi', 'mp4', 'webm', 'mkv'])])
    document = models.FileField(upload_to='documents', null=True)

    def __str__(self):
        return self.comment


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)

    def __str__(self):
        return self.post


class VerificationDetails(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=50)
    auth_otp = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     bridges = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)
#     photo = models.ImageField(upload_to="media",null=True, blank=True,)
#     background_photo = models.ImageField(upload_to="media",null=True, blank=True,)

#     def __str__(self):
#         return self.user.username


# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         user_profile = Profile(user=instance)
#         user_profile.save()
#         user_profile.bridges.set([instance.profile.id])
#         user_profile.save()

# post_save.connect(create_profile, sender=User)
