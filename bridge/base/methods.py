from random import randint
from django.conf import settings
from django.core.mail import send_mail
import uuid
from bridge.models import User


def createCode():
    count = 0
    code = ''
    while count < 5:
        codeValue = randint(0, 9)
        code += str(codeValue)
        count += 1
    return code


def timedifference(creationDate, currentDate):
        #d1 = datetime.strptime(creationDate, "%Y-%m-%d %H:%M:%S")
        #d2 = datetime.strptime(currentDate, "%Y-%m-%d %H:%M:%S")
        duration = currentDate-creationDate
        return abs(duration.total_seconds())

def sendSMS(phone_number, code):
    pass

def sendEmail(email, code):
    msg = f'Your verification code is {code}'
    send_mail( subject='BRIDGE VERIFICATION', message= msg,from_email=settings.EMAIL_HOST_USER, recipient_list=[email])
    print("message sent")
    return msg
    

def generate_username(email):
    # Generate a unique ID using the uuid module
    unique_id = str(uuid.uuid4().fields[-1])[:8]
    # Extract the first part of the email address as the username prefix
    username_prefix = email.split('@')[0]
    # Combine the prefix and unique ID to create the username
    username = f"{username_prefix}_{unique_id}"
    # Check if the username already exists, and add a number suffix if it does
    while User.objects.filter(username=username).exists():
        unique_id = str(uuid.uuid4().fields[-1])[:8]
        username = f"{username_prefix}_{unique_id}"
    return username

