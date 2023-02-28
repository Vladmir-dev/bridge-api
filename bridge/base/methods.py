from random import randint

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

def sendSMS():
    pass

def sendEmail():
    pass

