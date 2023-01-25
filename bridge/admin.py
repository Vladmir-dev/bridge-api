from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User

# class ProfileInline(admin.StackedInline):
#     model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    # Only display the "username" field
    fields = ['username', 'first_name', 'last_name', 'phone_number', 'email', 'sex', 'accepted_terms', 'date_of_birth', 'country', 'nationality', 'city', 'password']
    # inlines = [ProfileInline]
    
# Register your models here.
# admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# admin.site.register(Profile)
admin.site.unregister(Group)
