from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, EmailValidator
import uuid
from django_countries.fields import CountryField
from django.utils import timezone
import re
from django.utils.translation import gettext_lazy as _
import rstr
# from django.db.models.signals import post_save
# Create your models here.


def get_wallet_account_number():
    return rstr.xeger(r'[A-Z]\d\d[A-Z][A-Z]\d')


class User(AbstractBaseUser):
    uuid = models.CharField(max_length=100, editable=False,
                            null=False, blank=False, unique=True, default=uuid.uuid4)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(
        max_length=255, blank=True, null=True, unique=True,)
    phone_number = models.CharField(max_length=13, validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _(
            'Only numbers are allowed in format 000-000-000-000'), 'invalid')
    ], blank=True, unique=True)
    sex = models.CharField(max_length=30, blank=True, default="", choices=(
        ('Male', 'Male'), ('Female', 'Female'), ('Other', 'other')))
    date_joined = models.DateTimeField(default=timezone.now)
    accepted_terms = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    country = CountryField(blank=True)
    nationality = CountryField(blank=True)
    is_active = models.BooleanField(default=False)
    city = models.CharField(max_length=200, blank=True)
    token = models.CharField(max_length=1000, null=True)
    photo = models.ImageField(upload_to="media", null=True, blank=True)
    background_photo = models.ImageField(
        upload_to="media", null=True, blank=True)
    anonymous = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return self.username


class ChatMessage(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipient")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
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
        return "{o} wallet".format(self.user)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return self.comment


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)

    def __str__(self):
        return self.post


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
