import hashlib
import random
import string

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for char in range(5)])

def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt()
        _hash = hashlib.sha224(str.encode(password + salt)).hexdigest()
        return '{0}, {1}'.format(_hash, salt)

def check_pw_hash(password, _hash):
    salt = _hash.split(',')[1]
    if make_pw_hash(password, salt) == _hash:
        return True
    return False 