from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password: str):
    return ph.hash(password)

def verify_password(plaintext_password: str, hashed_password:str):
    try:
        return ph.verify(hashed_password, plaintext_password)
    except VerifyMismatchError:
      return False