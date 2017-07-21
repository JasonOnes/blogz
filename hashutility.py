import hashlib
import random
import string

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for char in range(5)])

def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt()
    salty_hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    _hash = hashlib.sha256(str.encode(password)).hexdigest()
    #return '{0}, {1}'.format(_hash, salt)
    return _hash

def check_pw_hash(password, _hash):
    #salt = _hash.split(',')[1]
    #_hash = _hash.split(',')[0]
    if make_pw_hash(password) == _hash:
        return True
    return False 
