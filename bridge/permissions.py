from .models import User
from rest_framework import authentication
from rest_framework import exceptions


class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', '')
        token = token.replace('Bearer ', '')
        if not token:
            return None

        try:
            user = User.objects.get(token=token)

        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)