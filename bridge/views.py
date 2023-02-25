from django.shortcuts import render
from rest_framework.response import Response
from .serialisers import BaseRegister, LoginSerializer, UserSerializer, TokenSerializer, PostSerializer, PostsSerializer, ProfileRegister
from rest_framework.viewsets import GenericViewSet
from rest_framework import exceptions as exc
from rest_framework.decorators import action
from rest_framework import status
import re
from rest_framework.exceptions import ValidationError
from .models import User, Wallet, Posts
from .services import emailValidator, sexValidator, get_token_for_account
from rest_framework.serializers import Serializer
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class AuthViewSet(GenericViewSet):

    serializer_class = Serializer

    def get_serializer_class(self):
        if self.action in ["register",]:
            return BaseRegister

        if self.action in ["login"]:
            return LoginSerializer

        return Serializer

    # def create(self, *args, **kwargs):
    # 	raise exc.NotSupported()

    # def list(self, *args, **kwargs):
    # 	raise exc.NotSupported()

    @action(detail=False, methods=['POST'])
    # @permission_classes([AllowAny])
    def register(self, request, **kwargs):
        serializer = BaseRegister(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HHTP_400_BAD_REQUEST)

        # check phone number
        # phone_number = serializer.data['phone_number']
        # print("number ===>", phone_number)
        # regex = re.compile(r'\d{12}')
        # if not (re.search(regex, phone_number)):
        #     raise ValidationError("Phone Number must be up to 12 digits")

        # check password
        password = serializer.data['password']
        print(password)
        if len(password) < 8:
            raise ValidationError("Password must be atleast 8 characters")

        # check if username already exists
        # username = serializer.data['username']
        # print("username ==>", username)
        # if username != None:
        #     CheckUsername = User.objects.filter(username=username)
        #     if CheckUsername:
        #         raise ValidationError("Username already exists")

        # check email
        email = serializer.data['email']
        print("email ==> ", email)
        emailValidator(email)

        # check country
        # country = serializer.data['country']
        # print("country ==>", country)
        # if len(country) != 2:
        #     raise ValidationError(
        #         "Country should be made up of 2 characters which are the initials of the country")

        # check accepted terms
        accepted_terms = serializer.data['accepted_terms']
        print("accepted terms ==>", accepted_terms)
        if accepted_terms in (None, False):
            raise ValidationError(
                "You must accept our terms of service and privacy policy")

        # create user
        user = User(first_name=serializer.data['first_name'],
                    last_name=serializer.data['last_name'], email=email, accepted_terms=accepted_terms)
        user.set_password(password)
        user.save()

        # get a token for account
        user.token = get_token_for_account(user, "authentication")
        user.save()

        # create wallet
        wallet = Wallet(user=user)
        wallet.save()

        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "sex": user.sex,
            "city": user.city,
            "date_of_birth": user.date_of_birth,
            'accepted_terms': user.accepted_terms,
            'date_joined': user.date_joined,
            "wallet": {
                "wallet_no": wallet.wallet_no,
                "amount": wallet.amount,
                "total_received": wallet.total_received,
                "total_sent": wallet.total_sent
            }
        }

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'], url_path="user_id/(?P<id>[0-9A-Za-z_\-]+)")
    def create_profile(self, request, id, *args, **kwargs):
        permission_classes = [IsAuthenticated,]
        serializer = ProfileRegister(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check user
        try:
            user = User.objects.filter(id=id)
        except:
            raise ValidationError("User does not exist")

        user = User.objects.get(id=id)

        # check phone number
        phone_number = serializer.data['phone_number']
        print("number ===>", phone_number)
        regex = re.compile(r'\d{12}')
        if not (re.search(regex, phone_number)):
            raise ValidationError("Phone Number must be up to 12 digits")

        # check if username already exists
        username = serializer.data['username']
        print("username ==>", username)
        if username != None:
            CheckUsername = User.objects.filter(username=username)
            if CheckUsername:
                raise ValidationError("Username already exists")

        sex = serializer.data['sex']
        city = serializer.data['city']
        date_of_birth = serializer.data['date_of_birth']

        user.phone_number = phone_number
        user.username = username
        user.sex = sex
        user.city = city
        user.date_of_birth = date_of_birth
        user.save()

        wallet = Wallet.objects.get(user=user)

        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "sex": user.sex,
            "city": user.city,
            "date_of_birth": user.date_of_birth,
            'accepted_terms': user.accepted_terms,
            'date_joined': user.date_joined,
            "wallet": {
                "wallet_no": wallet.wallet_no,
                "amount": wallet.amount,
                "total_received": wallet.total_received,
                "total_sent": wallet.total_sent
            }
        }

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def login(self, request, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            username = serializer.data['username']
            print("username ==>", username)
            password = serializer.data['password']
            print("password ==>", password)

            # check if username is phone number
            if username.isdecimal():
                try:
                    user = User.objects.get(phone_number=username)
                except:
                    data = {
                        "data": "failed credentials"
                    }
                    return Response(data, status=status.HTTP_401_UNAUTHORIZED)

                if user.check_password(password):
                    data = {
                        "token": user.token
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    data = {
                        "data": "failed credentials"
                    }
                    return Response(data, status=status.HTTP_401_UNAUTHORIZED)

            else:
                # check if it's an email address
                try:
                    user = User.objects.get(email=username)
                except:
                    try:
                        # check if it's a username
                        user = User.objects.get(username=username)
                    except:
                        data = {
                            "data": "failed credentials"
                        }
                        return Response(data, status=status.HTTP_401_UNAUTHORIZED)

                    if user.check_password(password):
                        data = {
                            "token": user.token
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {
                            "data": "failed credentials"
                        }
                        return Response(data, status=status.HTTP_401_UNAUTHORIZED)

                if user.check_password(password):
                    data = {
                        "token": user.token
                    }
                    return Response(data, status=status.HTTP_200_OK)

                else:
                    data = {
                        "data": "failed credentials"
                    }
                    return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path="user/(?P<id>[0-9A-Za-z_\-]+)")
    def get_user(self, request, id):

        # serializer
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # get user

        try:
            user = User.objects.filter(id=id)
        except:
            raise ValidationError("User does not exist")

        user = User.objects.get(id=id)

        # check wether token matches

        if user.token == serializer.data['token']:
            queryset = User.objects.filter(id=id).values()
            # user_serializer = UserSerializer(user)
            return Response(list(queryset), status=status.HTTP_200_OK)

        else:
            data = {
                "data": "failed credentials"
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['POST'], url_path="make_post")
    def make_post(self, request):

        # serializer
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # verify user

        try:
            user = User.objects.filter(token=serializer.data['token'])
        except:
            raise ValidationError("User does not exist")

        user = User.objects.get(token=serializer.data['token'])

        # print message
        print("this is the message =======>", serializer.data['message'])
        post = Posts(user=user, message=serializer.data['message'])
        post.save()

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'], url_path="get_posts/(?P<id>[0-9A-Za-z_\-]+)")
    def get_post(self, request, id):
        # serializer
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get user

        try:
            user = User.objects.filter(id=id)
        except:
            raise ValidationError("User does not exist")

        user = User.objects.get(id=id)

        # check wether token matches

        if user.token == serializer.data['token']:
            user_posts = Posts.objects.get(user=user)
            # print("==>",user_posts)
            post_serializer = PostsSerializer(user_posts)
            # print(post_serializer.data)
            # user_serializer = UserSerializer(user)
            return Response(post_serializer.data, status=status.HTTP_200_OK)

        else:
            data = {
                "data": "failed credentials"
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
