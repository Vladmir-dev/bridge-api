from rest_framework import serializers
from .models import User
from django_countries.serializers import CountryFieldMixin
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class BaseRegister(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'email', 'sex',
                  'accepted_terms', 'date_of_birth', 'country', 'nationality', 'city', 'password']
        # extra_kwargs = {'password': {'write_only': True,}}

        def validate_accepted_terms(self, value):
            if not value:
                raise ValidationError(
                    ("You must accept our terms of service and privacy policy"))
            return value


class UserSerializer(serializers.ModalSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'email', 'sex',
                  'accepted_terms', 'date_of_birth', 'country', 'nationality', 'city', 'password']
        extra_kwargs = {'password': {'write_only': True, }}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
