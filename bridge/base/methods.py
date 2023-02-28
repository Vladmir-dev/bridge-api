from random import randint
from django.conf import settings
from django.core.mail import send_mail

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
    

