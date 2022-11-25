from django.core import signing
import re


def emailValidator(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        
    if not (re.search(regex,email)):
        raise exc.BadRequest(_('invalid email address'))

def sexValidator(sex):
    sex= sex.lower()
    if sex != 'male' and sex != 'female':
        raise exc.BadRequest(_('invalid sex'))

def get_token_for_account(user, scope):
    """
    Generate a new signed token containing
    a specified account limited for a scope (identified as a string).
    """
    data = {"user_%s_id"%(scope):user.id}
    return signing.dumps(data)

def auth_response_data():
    pass