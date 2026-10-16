# Auth Service

![CI](https://github.com/Kevinbtseng/Auth-Service/actions/workflows/ci.yml/badge.svg)

An authentication API built with FastAPI. Users sign up and log in with a password, receive a short-lived JWT access token, and renew their session with rotating, single-use refresh tokens.

- **Stack:** FastAPI, PostgreSQL (SQLAlchemy 2 + Alembic), Redis, Docker, pytest
- **Interactive docs:** `/docs` once the service is running
- **CI/CD:** GitHub Actions runs the tests, then publishes a Docker image to GHCR

## Run it

1. Copy `.env.example` to `.env` and set `JWT_SECRET`. Generate one with:
   `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Start the services: `docker compose up -d --build`
3. Create the tables: `docker compose exec api alembic upgrade head`
4. Open http://127.0.0.1:8000/docs

Postgres is exposed on host port 5433 and Redis on 6379.

## API

| Method | Path | What it does |
|---|---|---|
| POST | `/auth/signup` | Create an account (201) |
| POST | `/auth/login` | Returns an access token and a refresh token |
| GET | `/auth/me` | Current user, requires `Authorization: Bearer <access token>` |
| POST | `/auth/refresh` | Exchange a refresh token for a new access and refresh token |
| POST | `/auth/logout` | Revoke the refresh token's whole session (204) |

## Security decisions and tradeoffs

### Decisions

1. **Argon2 password hashing and 15-minute JWTs.** Passwords are hashed with Argon2, which is purposefully slow so hashes are more expensive to crack. A short access-token lifetime limits the damage if one leaks. Tokens must include `exp` and `sub`, or they are rejected.
2. **Hashed refresh tokens.** Refresh tokens are random strings, not JWTs. Redis stores only their SHA-256 hash, so a Redis leak does not expose usable tokens.
3. **Rotation with reuse detection.** Each refresh token works once and is replaced by a new one. If an old token is used again, every token from the same login is revoked, which logs out both the thief and the victim of that session.
4. **Atomic single-use claim.** Checking and marking a token as used is simultaneously run on a single Redis Lua script, which means two simultaneous refreshes with the same token cannot both succeed. A test sends 10 concurrent claims and checks that exactly one wins.
5. **Login rate limiting and identical error messages.**  After 5 failed logins in 15 minutes for one IP and email, login returns 429. The limit is checked before the database lookup, so existing and non-existent emails are both blocked, and every authentication failure returns the same 401.

### Known limitations

1. **Access tokens cannot be revoked early.** Logout revokes refresh tokens, but an issued access token stays valid until it expires, up to 15 minutes. A denylist would fix this at the cost of a Redis lookup on every request.
2. **Blocking calls inside async routes.** The Redis and SQLAlchemy clients are synchronous but used inside `async def` routes, which blocks the event loop under load. Works fine at a smaller scale, and the fix is async clients or sync routes.
3. **Rate limiting is basic.** The rate limiter counts failures per IP and email in a fixed 15-minute window, which allows attackers to rotate IPs after 5 guesses.

## Testing and CI/CD

Create the test database once, then run the suite:

```
docker compose exec db psql -U postgres -c "CREATE DATABASE auth_test;"
pytest -v
```

Tests use the `auth_test` database and Redis DB 1.

On every push, GitHub Actions starts Postgres and Redis service containers and runs the suite. When tests pass on `main`, the workflow builds the Docker image and publishes it to `ghcr.io/kevinbtseng/auth-service`.
