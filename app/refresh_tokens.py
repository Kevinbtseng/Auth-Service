import secrets
import hashlib
from app.redis_client import r
import uuid

REFRESH_TOKEN_TTL = 7 * 24 * 3600

CLAIM_SCRIPT = """
if redis.call("hget", KEYS[1], "used") == "0" then
    redis.call("hset", KEYS[1], "used", "1")
    return 1
end
return 0
"""
_claim = r.register_script(CLAIM_SCRIPT)

def generate_token():
    return secrets.token_urlsafe(32)

def hash_token(raw_token):
    return hashlib.sha256(raw_token.encode()).hexdigest()

def store_refresh_token(user_id, family_id=None):
    if family_id is None:
        family_id = str(uuid.uuid4())

    raw_token = generate_token()
    hashed_token = hash_token(raw_token)

    key = f"refresh:{hashed_token}"
    family_key = f"family:{family_id}"

    pipe = r.pipeline()
    pipe.hset(key, mapping={"user_id": str(user_id), "family_id": family_id, "used": "0"})
    pipe.sadd(family_key, hashed_token)
    pipe.expire(key, REFRESH_TOKEN_TTL)
    pipe.expire(family_key, REFRESH_TOKEN_TTL)
    pipe.execute()

    return raw_token, family_id

def lookup_token(raw_token):
    key = f"refresh:{hash_token(raw_token)}"
    data = r.hgetall(key)
    
    return data or None

def revoke_family(family_id):
    family_key = f"family:{family_id}"

    tokens = r.smembers(family_key)

    for token in tokens:
        r.delete(f"refresh:{token}")
    r.delete(family_key)

def claim_token(raw_token):
    key = f"refresh:{hash_token(raw_token)}"
    return _claim(keys=[key]) == 1