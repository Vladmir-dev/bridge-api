from django.shortcuts import render
from rest_framework.response import Response
from .serialisers import BaseRegister, LoginSerializer, UserSerializer, TokenSerializer, ProfileRegister,PostSerializer,PostsSerializer, ChatSerializer,SendMoneySerializer,changePinSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework import exceptions as exc
from rest_framework.decorators import action
from rest_framework import status
import re
from rest_framework.exceptions import ValidationError
from .models import User, VerificationDetails, Posts, Wallet, ChatMessage, Notifications, ChatMessage, Likes, Comment, Reply,RelationShip
from .services import emailValidator, sexValidator, get_token_for_account
from rest_framework.serializers import Serializer
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
import json
from bridge.base.methods import createCode, timedifference, sendEmail, generate_username
from django.utils import timezone
from .permissions import CustomAuthentication
import hashlib
from django.conf import settings
import os

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
        phone_number = serializer.data['phone_number']
        # print("number ===>", phone_number)
        regex = re.compile(r'\d{12}')
        if not (re.search(regex, phone_number)):
            raise ValidationError("Phone Number must be up to 12 digits")

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
        # print("accepted terms ==>", accepted_terms)
        if accepted_terms in (None, False):
            raise ValidationError(
                "You must accept our terms of service and privacy policy")

        #username
        username = generate_username(email)
    
        # create user
        user = User.objects.create_user(username=username, first_name=serializer.data['first_name'], phone_number=phone_number,
                    last_name=serializer.data['last_name'], email=email, accepted_terms=accepted_terms, password=password)
        # user.set_password(password)
        user.save()
        print("user created")
        # get a token for account
        # user.token = get_token_for_account(user, "authentication")
        # user.save()

        # create wallet
        # wallet = Wallet(user=user)
        # wallet.save()

        wallet = Wallet.objects.get(user=user)
        hash_ = hashlib.sha256(wallet.wallet_no.encode()).hexdigest()
        print("This is the hash ===>",hash_)
        wallet.hash_value = hash_
        wallet.save()


        message = f"Your wallet number is {wallet.wallet_no} welcome to bridge"
        notific = Notifications(user=user, message=message)
        notific.save()

        code = createCode()
        print("code ===>", code)

        check_email = VerificationDetails.objects.filter(
            email=email)

        if check_email:
            check_email.update(
                auth_otp=code, date_created=timezone.now())
            sendEmail(email, code)

        else:
            verification = VerificationDetails(
                email=user.email, auth_otp=code)
            sendEmail(email, code)
        
        # wallet = Wallet.objects.get(user=user)

        # phone_number = '+' + phone_number
        # message = "Your Verification code is" + code

        # check_phone_number = VerificationDetails.objects.filter(
            # phone_number=phone_number)

        # if check_phone_number:
            # check_phone_number.update(
                # auth_otp=code, date_created=timezone.now())
            # send sms

        # else:
            # verification = VerificationDetails(
                # phone_number=user.phone_number, auth_otp=code)
            # send sms

        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "sex": user.sex,
            "city": user.city,
            "verified": user.verified,
            "occupation":user.occupation,
            "interests":user.interests,
            "country":user.country,
            "nationality": user.nationality,
            "date_of_birth": user.date_of_birth,
            'accepted_terms': user.accepted_terms,
            'date_joined': user.date_joined,
            "wallet": {
                "wallet_no": wallet.wallet_no,
                "hash_value":wallet.hash_value,
                "amount": wallet.amount,
                "total_received": wallet.total_received,
                "total_sent": wallet.total_sent
            }
        }

        return Response(data,status=status.HTTP_201_CREATED)
    
    

    @action(detail=False, methods=['POST'], url_path="user_id/(?P<id>[0-9A-Za-z_\-]+)")
    def create_profile(self, request, id, *args, **kwargs):
        permission_classes = [IsAuthenticated,]
        serializer = ProfileRegister(data=request.data)

        if serializer.is_valid():

            # check user
            try:
                user = User.objects.filter(id=id)
            except:
                raise ValidationError("User does not exist")

            user = User.objects.get(id=id)

            # check if username already exists
            username = serializer.validated_data.get('username')
            print("username ==>", username)
            if username != None:
                CheckUsername = User.objects.filter(username=username)
                if CheckUsername:
                    raise ValidationError("Username already exists")

            sex = serializer.validated_data.get('sex')

            city = serializer.validated_data.get('city')
            country = serializer.validated_data.get('country')
            nationality = serializer.validated_data.get('nationality')
            date_of_birth = serializer.validated_data.get('date_of_birth')
            photo = serializer.validated_data.get('photo')  
            occupation = serializer.validated_data.get('occupation')
            interests = serializer.validated_data.get('interests')
            # user.phone_number = phone_number
            if photo is None or photo == '':
                # path = '/default/default.jpeg'
                photo = ''
            else:
                photo = photo

            if username != None:
                user.username = username

            if sex != None:
                user.sex = sex

            if city != None:
              user.city = city

            if date_of_birth != None:
                user.date_of_birth = date_of_birth
            
            if country != None:
                user.country = country

            if nationality != None:
                user.nationality = nationality

            if photo != None:
                user.photo = photo
            
            if occupation != None:
                user.occupation = occupation
            
            if interests != None:
                user.interests = interests

            user.save()

            wallet = Wallet.objects.get(user=user)
            
            

            # query_set = UserSerializer(user)
            # print(query_set)

            data = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "sex": user.sex,
                "city": user.city,
                "verified": user.verified,
                "interests":user.interests,
                "occupation":user.occupation,
                "photo":photo,
                "country": user.country,
                "nationality": user.nationality,
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
        else:
            return Response(serializer.errors)
         

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
                    # token = Token.objects.get(user=user)
                    data = {
                        "token": user.token,
                        "verified": user.verified
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
                        # token = Token.objects.get(user=user)
                        # print("User token",user)
                        data = {
                            "token": user.token,
                            "verified": user.verified
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {
                            "data": "failed credentials"
                        }
                        return Response(data, status=status.HTTP_401_UNAUTHORIZED)

                if user.check_password(password):
                    # token = Token.objects.get(user=user)
                    data = {
                        "token":user.token,
                        "verified": user.verified
                    }
                    return Response(data, status=status.HTTP_200_OK)

                else:
                    data = {
                        "data": "failed credentials"
                    }
                    return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



    @action(detail=False, methods=['GET'], url_path="user",)
    def get_user(self, request):
        
        # serializer
        # serializer = TokenSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # get user
        user_token = request.META.get('HTTP_AUTHORIZATION', '')
        user_token = user_token.replace('Bearer ', '')
        # user_token = str(user_token)
        print("this is the token", user_token)

        try:
            user = User.objects.filter(token=user_token)
        except:
            raise ValidationError("User does not exist")

        user = User.objects.get(token=user_token)
        
        if user.photo is None or user.photo == "":
            photo = " "
        else:
            photo = user.photo
        # check wether token matches
        photo = str(photo)
        print("photo ===> ", photo)

        total_posts = Posts.objects.filter(user=user).count()
        total_comments = Comment.objects.filter(user=user).count()
        total_likes = Likes.objects.filter(user=user).count()
        total_replies = Reply.objects.filter(user=user).count()
        posts_and_replies = total_posts + total_replies

        #folowers
        followers = RelationShip.objects.filter(followed=user).count()
        #follows
        follows = RelationShip.objects.filter(follower=user).count()

        # print("total posts ===>",user_posts)        
        # if user.token == serializer.data['token']:
        # queryset = User.objects.filter(token=user_token).values()
        # queryset = User.objects.get(token=user_token)
        # print(dict(queryset))
        # user_serializer = UserSerializer(user)
        # print(user_serializer.data)
        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "sex": user.sex,
            "city": user.city,
            "verified": user.verified,
            "photo":photo,
            "country": user.country,
            "interests":user.interests,
            "nationality": user.nationality,
            "date_of_birth": user.date_of_birth,
            'accepted_terms': user.accepted_terms,
            'date_joined': user.date_joined,
            'total_posts': total_posts,
            'total_comments':total_comments,
            'total_likes':total_likes,
            'total_replies':total_replies,
            'posts_and_replies':posts_and_replies,
            'followers':followers,
            'follows':follows

        }

        return Response(data, status=status.HTTP_200_OK)

    

    @action(detail=False, methods=['GET'], url_path="allusers",)
    def get_users(self, request):
        permission_classes = [IsAuthenticated,] 
        user_token = request.META.get('HTTP_AUTHORIZATION', '')
        user_token = user_token.replace('Bearer ', '')
        # user_token = str(user_token)
        print("this is the token", user_token)

        try:
            user = User.objects.filter(token=user_token)
        except:
            raise ValidationError("User does not exist")

        users = User.objects.values()

        # check wether token matches

        # if user.token == serializer.data['token']:
        # queryset = User.objects.filter(token=user_token).values()
            # user_serializer = UserSerializer(user)
        return Response(users, status=status.HTTP_200_OK)

      

    @action(detail=False, methods=["GET"], url_path="wallet_balance/(?P<id>[0-9A-Za-z_\-]+)")
    def check_balance(self, request,id, **kwargs):
        permission_classes = [IsAuthenticated,]
        try:
            user = User.objects.filter(id=id)
        except:
            data = {
                'status': 'failed',
                'details': 'User does not exist'
            }
            return Response(data, status = status.HTTP_403_FORBIDDEN)
        
        user = User.objects.get(id=id)
        # print(user.username)
        wallet = Wallet.objects.get(user=user)
        # accountBalance = getUser.amount
        data = {
            'amount': wallet.amount
        }
        return Response(data, status = status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="notifications/(?P<id>[0-9A-Za-z_\-]+)")
    def get_notifications(self, request, id, **kwargs):
        # permission_classes = [IsAuthenticated,]
        
        try:
            user = User.objects.get(id=id)
        except:
            raise ValidationError("User doesnot exist")
        
        notifications = Notifications.objects.filter(user=user).values()
        return Response(notifications, status=status.HTTP_200_OK)



    @action(detail=False, methods=["POST"], url_path="send_money/(?P<id>[0-9A-Za-z_\-]+)")
    def send_money(self, request, id, **kwargs):
        permission_classes = [IsAuthenticated,]
        serializer = SendMoneySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:

            sender = User.objects.get(id=id)
        except:
            raise ValidationError("User doesnot exist")

        sender_wallet = Wallet.objects.get(user=sender)

        #king1ssem_10940414
        #kingssem_88495250

        try:

            reciever = User.objects.get(username=serializer.data['receiver'])
        except:
            raise ValidationError("User doesnot exist")

        reciever_wallet = Wallet.objects.get(user=reciever)
        
        #check if sender has sufficent amount
        print("sender amount ==>", float(sender_wallet.amount))
        print("amount to send ==>", float(serializer.data['amount']))
        print("difference", float(sender_wallet.amount) - float(serializer.data['amount']))
        difference = float(sender_wallet.amount) - float(serializer.data['amount'])

        if difference > 0:

            sender_wallet.amount -=  serializer.data['amount']
            sender_wallet.total_sent += serializer.data['amount']
            sender_wallet.save(update_fields=['amount','total_sent'])

            reciever_wallet.amount +=  serializer.data['amount']
            reciever_wallet.total_received += serializer.data['amount']
            reciever_wallet.save(update_fields=['amount','total_received'])
            
            sender_msg = f"You sent UGX {serializer.data['amount']} to {reciever.username} current balance is UGX {sender_wallet.amount}"
            sender_not = Notifications(user=sender, message=sender_msg)
            sender_not.save()

            reciever_msg = f"You have received {serializer.data['amount']} from {sender.username} current balance is UGX {reciever_wallet.amount}"
            reciever_not = Notifications(user=reciever, message=sender_msg)
            reciever_not.save()

            # transaction = Transactions(sender=getSender.username, amount=serializer.data['amount'], receiver=receiver.username,status='complete', trans_type='send')
            # transaction.save()

            # res = "{0} has received {1} UGX from {2}  remaining balance {3}".format(reciever_wallet.wallet_no,serializer.data['amount'], sender.username, reciever_wallet.amount)
            data = {
                "status":"successfull",
                "details": f"succesfully sent {serializer.data['amount']} to {serializer.data['receiver']}"
            }

        else:
            data = {
                'status': 'failed',
                'details': 'Insuficient funds'
            }
            sender_msg = f"You have insuficient funds to complete this transaction"
            sender_not = Notifications(user=sender, message=sender_msg)
            sender_not.save()

        return Response(data, status=status.HTTP_200_OK)
     

    # @action(detail=False, methods=['POST'], url_path="make_post")
    # def make_post(self, request):

    #     # serializer
    #     serializer = PostsSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     # verify user

    #     try:
    #         user = User.objects.filter(token=serializer.data['token'])
    #     except:
    #         raise ValidationError("User does not exist")

    #     user = User.objects.get(token=serializer.data['token'])

    #     # print message
    #     print("this is the message =======>", serializer.data['message'])
    #     post = Posts(user=user, message=serializer.data['message'])
    #     post.save()

    #     return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"], url_path="change_password/(?P<id>[0-9A-Za-z_\-]+)")
    def change_password(self, request,id, **kwargs):
        permission_classes = [IsAuthenticated, ]
        serializer = changePinSerializer(data= request.data)
        if serializer.is_valid(raise_exception=True):
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']
            #check new pin if its a pin
            # if not new_password.isdecimal() or len(new_password) != 5:
                # raise exc.BadRequest(_('New pin must be made up of five digits'))

            try:
                getUser = User.objects.get(id= id)
            except:
                data = {
                    'status': 'failed',
                    'detail': 'User with that id does not exist'
                }
                return Response(data, status = status.HTTP_401_UNAUTHORIZED)

            if not getUser.check_password(current_password):
                data = {
                    'status': 'failed',
                    'detail': 'current password is incorrect'
                }
                return Response(data, status = status.HTTP_401_UNAUTHORIZED)

            getUser.set_password(new_password)
            getUser.save()

            data = {
                'status': 'successful',
                'detail': 'Pin was changed successfully'
            }
            return Response(data, status = status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False,methods=["POST"], url_path="send_otp")
    def sendOTP(self, request, **kwargs):
        #field to authenticate
        fieldToAuthenticate = request.data.get("verificationField")
        if fieldToAuthenticate is None or fieldToAuthenticate =="":
            data ={
                'error': 'check verificationField for errors'
                }
            return Response(data, status = status.HTTP_403_FORBIDDEN)
        
        #check field in list
        verifyList = ['email', 'phone_number']
        if not fieldToAuthenticate in verifyList:
            data = {
                'status': 'failed', 
                'detail': 'wrong verificationField'
            }
            return Response(data, status = status.HTTP_403_FORBIDDEN)
        
        # # fieldsValidator(fieldToAuthenticate, 'verificationDetails')
        # if fieldToAuthenticate == 'phone_number':
        #     phoneNumber = request.data.get("phone_number")
        #     if phoneNumber is None or phoneNumber =="":
        #         data ={
        #             'error': 'check phone Number field for errors'
        #             }
        #         return Response(data, status = status.HTTP_403_FORBIDDEN)
            
        #     checkPhoneNumberInDb = User.objects.filter(phone_number= phoneNumber)
        #     if not checkPhoneNumberInDb:
        #         data = {
        #             'status': 'failed',
        #             'detail': 'there is no account with that phone number'
        #         }
        #         return Response(data, status = status.HTTP_401_UNAUTHORIZED)
            
        #     #generate random code
        #     authOTP= createCode()
        #     print(authOTP)
        #     #if instance is already there just update otp
        #     checkPhoneNumber = VerificationDetails.objects.filter(phone_number= phoneNumber)
        #     if checkPhoneNumber:
        #         currentTime = timezone.now()
        #         checkPhoneNumber.update(auth_otp = authOTP, date_created= currentTime)
        #         phoneNumber = '+'+ phoneNumber
        #         message = 'Your verification code is '+ authOTP
        #         # sendSMS(phoneNumber,message)
        #         data = {
        #             'status': 'success',
        #             'detail': 'OTP sent'
        #         }
        #         return Response(data, status = status.HTTP_200_OK)
            
        #     #register otp in database
        #     registerOTP = VerificationDetails(phone_number = phoneNumber, otp = authOTP)
        #     registerOTP.save()
        #     #send sms
        #     phoneNumber = '+'+ phoneNumber
        #     message = 'Your verification code is '+ authOTP
        #     sendSMS(phoneNumber, message)

    
        #     data = {
        #         'status': 'success',
        #         'detail': 'OTP sent'
        #         }
        #     return Response(data, status = status.HTTP_200_OK)
        

        email = request.data.get("email")
        if email is None or email =="":
            data ={
                'error': 'check email field for errors'
                }
            return Response(data, status = status.HTTP_403_FORBIDDEN)
        # checkEmailInDb = Account.objects.filter(email = email)
        # if not checkEmailInDb:
        #     data = {
        #         'status': 'failed',
        #         'detail': 'there is no account with that email'
        #         }
        #     return JsonResponse(data, status = status.HTTP_401_UNAUTHORIZED)

        #generate random code
        authOTP= createCode()
        #if instance is already there just update otp
        checkEmail = VerificationDetails.objects.filter(email= email)
        if checkEmail:
            currentTime = timezone.now()
            checkEmail.update(auth_otp = authOTP, date_created= currentTime)
            email = email
            message = 'Your verification code is '+ authOTP
            sendEmail(email, authOTP)

            data = {
                'status': 'success',
                'detail': 'OTP sent'
                }
            return Response(data, status = status.HTTP_200_OK)
        
        #register otp in database
        registerOTP = VerificationDetails(email = email, auth_otp = authOTP)
        registerOTP.save()
        #send email
        email = email
        message = 'Your verification code is '+ authOTP
        sendEmail(email,authOTP)
        data = {
            'status': 'success',
            'detail': 'OTP sent'
            }
        return Response(data, status = status.HTTP_200_OK)    


    @action(detail=False, methods=["POST"])
    def verifyOTP(self, request, **kwargs):
        # phoneNumber = request.data.get("phoneNumber")
        otp = request.data.get("otp")
        if otp is None or otp == "":
            data = {
                'error': 'check otp field for errors'
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        
        verificationField = request.data.get("verificationField")

        if verificationField is None or verificationField == "":
            data = {
                'error': 'check verificationField for errors'
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        
        verifyList = ['email', 'phoneNumber']

        if not verificationField in verifyList:
            data = {
                'status': 'failed',
                'detail': 'wrong verificationField'
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        if verificationField == 'phoneNumber':
            phoneNumber = request.data.get("phoneNumber")
            if phoneNumber is None or phoneNumber == "":
                data = {
                    'error': 'check phoneNumber field for errors'
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
            # phone number exists in the system
            # checkPhoneNumberInDb = Account.objects.filter(phone_number= phoneNumber)
            # if not checkPhoneNumberInDb:
            #     data = {
            #         'status': 'failed',
            #         'detail': 'there is no account with that phone number'
            #     }
            #     return JsonResponse(data, status = status.HTTP_401_UNAUTHORIZED)

            # check if phoneNumber in otp exists
            checkPhoneNumber = VerificationDetails.objects.filter(
                phone_number=phoneNumber)
            if not checkPhoneNumber:
                data = {
                    'status': 'failed',
                    'detail': 'this phone number has no otp related with it'
                }
                return Response(data, status=status.HTTP_401_UNAUTHORIZED)
            # get the object using phoneNumber and check if its the correct otp
            getOtp = VerificationDetails.objects.get(phone_number=phoneNumber)
            if getOtp.auth_otp != otp:
                data = {
                    'status': 'failed',
                    'detail': 'incorect otp'
                }
                return Response(data, status=status.HTTP_401_UNAUTHORIZED)
            # if true check if its not expired
            # # expiration time is 15minutes
            getDate = getOtp.date_created
            expirationTime = 12*60
            currentTime = timezone.now()
            # check code if its still valid
            timeInSec = timedifference(getDate, currentTime)
            if timeInSec <= expirationTime:
                # update is_phone_verified
                update_is_phone_verified = User.objects.filter(phone_number=phoneNumber).update(
                    verified=True)
                data = {
                    'status': 'success',
                    'detail': 'user validated'
                }
                return Response(data, status=status.HTTP_200_OK)
            data = {
                'status': 'failed',
                'detail': 'otp expired'
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

        email = request.data.get("email")
        if email is None or email == "":
            data = {
                'error': 'check email field for errors'
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        # phone number exists in the system
        # checkEmailInDb = Account.objects.filter(email = email)
        # if not checkEmailInDb:
        #     data = {
        #         'status': 'failed',
        #         'detail': 'there is no account with that Email'
        #         }
        #     return JsonResponse(data, status = status.HTTP_401_UNAUTHORIZED)

        # check if email in otp table exists
        checkEmail = VerificationDetails.objects.filter(email=email)
        if not checkEmail:
            data = {
                'status': 'failed',
                'detail': 'this email has no otp related with it'
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        # get the object using phoneNumber and check if its the correct otp
        getOtp = VerificationDetails.objects.get(email=email)
        if getOtp.auth_otp != otp:
            data = {
                'status': 'failed',
                'detail': 'incorect otp'
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        # if true check if its not expired
        # expiration time is 15minutes
        getDate = getOtp.date_created
        expirationTime = 15*60
        currentTime = timezone.now()
        # check code if its still valid
        timeInSec = timedifference(getDate, currentTime)
        if timeInSec <= expirationTime:
            # update is_phone_verified
            update_verified = User.objects.filter(
                email=email).update(verified=True)
            data = {
                'status': 'success',
                'detail': 'email validated'
            }
            return Response(data, status=status.HTTP_200_OK)
        data = {
            'status': 'failed',
            'detail': 'otp expired'
        }
        return Response(data, status=status.HTTP_401_UNAUTHORIZED)



class PostCreateView(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    authentication_classes = [CustomAuthentication,]
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Posts.objects.filter(user=user)


class ChatCreateView(generics.ListCreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatSerializer
    authentication_classes = [CustomAuthentication,]
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(user=user)
