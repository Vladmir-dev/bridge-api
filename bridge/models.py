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
import random
from django_mysql.models import ListCharField
# from django.db.models.signals import post_save
# Create your models here.

# default = "/media/user/photo/default/default.jpeg"

def get_wallet_account_number():
    #get the Prefix
    prefix = "BRI"

    #follow the three letters with a four digit number
    number = str(random.randint(1000, 9999))

    #calculate checksum
    checksum = str(sum(int(float(digit)) for digit in number) % 10)

    #Append the checksum to the end of the account number
    account_number = prefix + number + checksum
    print("account_number ==>", account_number)

    return account_number



def get_user_photo_file_path(instance, filename):
    return get_file_path(instance, filename, "user/photo")


# def get_id():
#     pass

def generate_token():
    dt = datetime.now() + timedelta(days=60)
    
    payload = {
        # 'id':self.pk,
        'exp':int(dt.strftime('%s'))
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    print("token======>", token)
    
    return token



def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def compress_img(image_name, new_size_ratio=0.5, quality=90, width=None, height=None, to_jpg=False):
        #load the image to memory
        img = Image.open(image_name.path)

        #print the original image shape
        print("[*] Image Shape: ", img.size)

        # get the original image size in bytes
        image_size = os.path.getsize(image_name.path)
        print("[*] Size before compression:", get_size_format(image_size))

        #begin compression with ratio
        if new_size_ratio < 1.0:
            #if resizing is below 1 then multiply width & height with this ratio to reduce the image size
            img =  img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)

            #print new image shape
            print("[+] New Image Shape: ", img.size)
        
        elif width and height:
            #if image and height are set resize them instead
            img = img.resize((width, height))
            
            #print the new image shape
            print("[+] New Image Shape: ", img.size)

        # #split the filename and extension
        # filename, ext = os.path.splitext(image_name)

        # if to_jpg:
        #     #change the extension to jpg
        #     new_filename = f"{filename}_compressed.jpg"
        # else:
        #     new_filename = f"{filename}_compressed{ext}"

        # img.save(image_name.path, quality=quality, optimize=True)
        # get the image size after compression in bytes
        

        try:
            #save the image with the corresponding quality and optimize set to True
            img.save(image_name.path, quality=quality, optimize=True)
            image_size = os.path.getsize(image_name.path)
            print("[+] Size After compression:", get_size_format(image_size))
        except OSError:
            #convert the image to RGB mode first
            img = img.convert("RGB")
            img.save(image_name.path, quality=quality, optimize=True)



class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be set")
        
        if not email:
            raise ValueError("Email field must be set")
        
        email = self.normalize_email(email)
        extra_fields['token'] = generate_token()
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        wallet = Wallet(user=user)
        wallet.save()
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
    sex = models.CharField(max_length=30, blank=True,null=True, default="", choices=(
        ('Male', 'Male'), ('Female', 'Female'), ('Other', 'other')))
    bio = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    accepted_terms = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    token = models.CharField(max_length=550, null=True, blank=True, unique=True)
    photo = models.ImageField(
        upload_to=get_user_photo_file_path, null=True, blank=True)
    background_photo = models.ImageField(
        upload_to=get_user_photo_file_path, null=True, blank=True)
    occupation = models.CharField(max_length=250, null=True, blank=True)
    interests = ListCharField(base_field=models.CharField(max_length=100), size=1000, max_length=(1000 * 101), blank=True, null=True)
    anonymous = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username}"

    # @property
    # def token(self):
    #     return self.generate_token()


    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.photo:
            compress_img(self.photo)
        #     img = Image.open(self.photo)
        #     width = img.width
        #     height = img.height
        #     print(f'width: {width}, height: {height}')
        
        # SIZE = (300, 300)

        # if self.photo:
        #     img = Image.open(self.photo.path)
        #     img.thumbnail(SIZE)
        #     img.save(self.photo.path)

        # for field_name in ['photo', 'background_photo']:
        #     field = getattr(User, field_name)
        #     if field:
        #         img = Image.open(field)
        #         img.thumbnail(SIZE)
        #         img.save(self.field_name.path)
    

    



    



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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            compress_img(self.photo)
            

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.photo:
            compress_img(self.photo)

class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    message = models.TextField()
    photo = models.ImageField(upload_to=get_user_photo_file_path, null=True, blank=True)
    video = models.FileField(upload_to='videos', null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi', 'mp4', 'webm', 'mkv'])])
    document = models.FileField(upload_to='documents', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{0} : {1}".format(self.user, self.message)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.photo:
            compress_img(self.photo)


class RelationShip(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed")
    

class Bridges(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bridger1")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bridger2")


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    wallet_no = models.CharField(_('Account Number'), max_length=10, unique=True, default=get_wallet_account_number)
    hash_value = models.CharField(max_length=2000),
    total_sent = models.FloatField(default=0)
    total_received = models.FloatField(default=0)
    password = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wallet_no


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    comment = models.TextField()
    photo = models.ImageField(upload_to=get_user_photo_file_path, null=True, blank=True)
    video = models.FileField(upload_to='videos', null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi', 'mp4', 'webm', 'mkv'])])
    document = models.FileField(upload_to='documents', null=True)

    def __str__(self):
        return self.comment
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        compress_img(self.photo)


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)

    def __str__(self):
        return self.post

class Drops(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creater")
    receipients = models.ManyToManyField(User, related_name='received_posts', blank=True)
    message = models.CharField(max_length=1000)
    photo = models.ImageField(upload_to=get_user_photo_file_path, null=True, blank=True)
    video = models.FileField(upload_to='videos', null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi', 'mp4', 'webm', 'mkv'])])
    document = models.FileField(upload_to='documents', null=True)

    def __str__(self):
        return f"Post {self.id} by {self.sender.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        compress_img(self.photo)

class VerificationDetails(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=50)
    auth_otp = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)


class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.message

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
