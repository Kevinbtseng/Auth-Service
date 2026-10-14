from app.redis_client import r

MAX_FAILURES = 5
WINDOW_SECONDS = 900

def _key(ip, email):
    return f"ratelimit:login:{ip}:{email.lower()}"

def is_blocked(ip, email):
    count = int(r.get(_key(ip, email)) or 0)

    return count >= MAX_FAILURES

def record_failure(ip, email):
    key = _key(ip, email)

    count = r.incr(key)

    if count == 1:
        r.expire(key, WINDOW_SECONDS)

    return count

def clear_failures(ip, email):
    key = _key(ip, email)

    r.delete(key)


def retry_after(ip, email):
    key = _key(ip, email)

    return r.ttl(key)