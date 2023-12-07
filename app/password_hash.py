import hashlib


def hash_password(password):
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed_password


def check_password(hashed_password, user_password):
    return hashed_password == hashlib.sha256(user_password.encode('utf-8')).hexdigest()