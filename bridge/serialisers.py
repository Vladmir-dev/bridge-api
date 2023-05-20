from rest_framework import serializers
from .models import User, Posts, ChatMessage,Comment,Drops, DropLikes, DropComment
from django_countries.serializers import CountryFieldMixin
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class BaseRegister(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number',
                  'email', 'accepted_terms', 'password']
        # extra_kwargs = {'password': {'write_only': True,}}

        def validate_accepted_terms(self, value):
            if not value:
                raise ValidationError(
                    ("You must accept our terms of service and privacy policy"))
            return value


class ProfileRegister(serializers.ModelSerializer):
    interests = serializers.ListField(child=serializers.CharField(), required=False)
    photo = serializers.ImageField(required=True)
    class Meta:
        model = User
        fields = ['username',  'sex', 'date_of_birth',
                  'country', 'nationality', 'city', 'photo', 'occupation', 'interests', 'bio']
        # extra_kwargs = {'password': {'write_only': True,}}

    def update(self, instance, validated_data):
        photo = validated_data.pop('photo', None)
        instance = super().update(instance, validated_data)
        
        if photo:
            instance.photo = photo
            instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    # country = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'email', 'sex',
                  'accepted_terms', 'date_of_birth', 'country', 'nationality', 'city', 'password', 'verified',]
        extra_kwargs = {'password': {'write_only': True, }}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class PostSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    message = serializers.CharField(required=True)


class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = "__all__"

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class SendMoneySerializer(serializers.Serializer):
    receiver = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)


class changePinSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class WalletPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    # new_password = serializers.CharField(required=True)


class DropsSerializer(serializers.ModelSerializer):
    receipients = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(is_staff=False))
    
    class Meta:
        model = Drops
        fields = ['sender', 'receipients', 'message', 'photo', 'video', 'document', ]


class DropCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropComment
        fields = "__all__"


class ProfilePhotSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['photo']