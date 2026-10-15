from app.security import hash_password, verify_password, create_access_token, decode_access_token
from app import config
from datetime import timedelta, datetime, timezone
import secrets
import jwt

def test_hash_salting():
    assert hash_password("123") != hash_password("123")

def test_verify_password():
    hashed_password = hash_password("123")

    assert verify_password("123", hashed_password)
    assert not verify_password("321", hashed_password)

def test_access_encode_decode():    
    token = create_access_token({"sub": "123"})
    
    assert decode_access_token(token)["sub"] == "123"

def test_expired_token_rejection():
    token = create_access_token({"sub": "123"}, expires_delta=timedelta(seconds=-1))
    
    assert decode_access_token(token) is None

def test_changed_token_signature():
    token = create_access_token({"sub": "123"})

    header, payload, signature = token.split(".")

    if signature[0] == "a":
        flipped = "b"
    else:
        flipped = "a"

    changed_token = ".".join([header, payload, flipped + signature[1:]])

    assert decode_access_token(changed_token) is None

def test_wrong_jwt_secret():
    random_secret = secrets.token_bytes(256)
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    payload = {"sub": "123", 
               "exp": expire, 
               "iat": datetime.now(timezone.utc)
               }

    wrong_token = jwt.encode(
        payload,
        random_secret,
        algorithm="HS256"
    )

    assert decode_access_token(wrong_token) is None

def test_token_without_exp_rejected():
    token = jwt.encode({"sub": "123"}, config.JWT_SECRET, algorithm="HS256")

    assert decode_access_token(token) is None

def test_token_without_sub_rejected():
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    token = jwt.encode({"exp": expire}, config.JWT_SECRET, algorithm="HS256")

    assert decode_access_token(token) is None