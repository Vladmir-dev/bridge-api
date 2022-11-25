from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, EmailValidator
import uuid
from django_countries.fields import CountryField
from django.utils import timezone
import re
from django.utils.translation import gettext_lazy as _
# Create your models here.

class User(AbstractBaseUser):
    uuid = models.CharField(max_length=100, editable=False, null=False, blank=False, unique=True, default=uuid.uuid4)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=255,blank=True, null= True, unique=True,)
    phone_number = models.CharField(max_length=13,validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _('Only numbers are allowed in format 000-000-000-000'), 'invalid')
        ],blank=True, unique=True)
    sex = models.CharField(max_length=30,blank=True, default="",choices=(('Male', 'Male'), ('Female', 'Female'),('Other', 'other')))
    date_joined = models.DateTimeField(default=timezone.now)
    accepted_terms = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    country = CountryField(blank=True)
    nationality = CountryField(blank=True)
    city = models.CharField(max_length=200, blank=True)
    token = models.CharField(max_length=1000, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()
