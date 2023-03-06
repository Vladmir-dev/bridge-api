from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Wallet, Posts, VerificationDetails, Likes, Comment

# class ProfileInline(admin.StackedInline):
#     model = Profile

# class UserAdmin(admin.ModelAdmin):
    # model = User
    # Only display the "username" field
    # fields = ['username', 'first_name', 'last_name', 'phone_number', 'email', 'sex', 'accepted_terms', 'date_of_birth', 'country', 'nationality', 'city', 'password', 'photo', 'background_photo', 'token', 'verified']
    # inlines = [ProfileInline]
    
# Register your models here.
# admin.site.unregister(User)
admin.site.register(User)
admin.site.register(Wallet)
admin.site.register(Posts)
admin.site.register(VerificationDetails)
admin.site.register(Likes)
admin.site.register(Comment)
