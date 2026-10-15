from datetime import datetime, timedelta, timezone

import jwt
from fastapi import status

from app import config


def forged_token(claims):
    return jwt.encode(claims, config.JWT_SECRET, algorithm="HS256")


def me(client, token):
    return client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})


def future():
    return datetime.now(timezone.utc) + timedelta(minutes=15)


def test_me_with_valid_token(client, login_tokens):
    response = me(client, login_tokens["access_token"])
    assert response.status_code == status.HTTP_200_OK


def test_non_numeric_sub_returns_401(client):
    token = forged_token({"sub": "abc", "exp": future()})

    assert me(client, token).status_code == status.HTTP_401_UNAUTHORIZED


def test_non_string_sub_returns_401(client):
    token = forged_token({"sub": ["1"], "exp": future()})

    assert me(client, token).status_code == status.HTTP_401_UNAUTHORIZED


def test_missing_sub_returns_401(client):
    token = forged_token({"exp": future()})

    assert me(client, token).status_code == status.HTTP_401_UNAUTHORIZED
