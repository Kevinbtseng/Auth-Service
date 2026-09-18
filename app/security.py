from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone
from app import config

ph = PasswordHasher()

def hash_password(password: str):
    return ph.hash(password)

def verify_password(plaintext_password: str, hashed_password: str):
    try:
        return ph.verify(hashed_password, plaintext_password)
    except VerifyMismatchError:
      return False

def create_access_token(data: dict, expires_delta: timedelta=None):
    to_encode = data.copy()


    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })

    encoded_jwt = jwt.encode(
        to_encode, 
        config.JWT_SECRET, 
        algorithm="HS256"
    )
    return encoded_jwt

def decode_access_token(token: str):
    try:
        return jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    except PyJWTError:
        return None