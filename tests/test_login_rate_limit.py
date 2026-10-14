from fastapi import status
from app import rate_limit


def wrong_login(client, email):
    return client.post("/auth/login", json={"email": email, "password": "wrong-password"})


def test_blocked_after_max_failures(client, registered_user):
    for _ in range(rate_limit.MAX_FAILURES):
        response = wrong_login(client, registered_user["email"])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    blocked_response = wrong_login(client, registered_user["email"])
    assert blocked_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert int(blocked_response.headers["Retry-After"]) > 0


def test_success_resets_counter(client, registered_user):
    for _ in range(rate_limit.MAX_FAILURES - 1):
        wrong_login(client, registered_user["email"])

    good_response = client.post("/auth/login", json=registered_user)
    assert good_response.status_code == status.HTTP_200_OK

    for _ in range(rate_limit.MAX_FAILURES - 1):
        response = wrong_login(client, registered_user["email"])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_other_email_not_affected(client, registered_user):
    for _ in range(rate_limit.MAX_FAILURES):
        wrong_login(client, registered_user["email"])

    other_response = wrong_login(client, "someone-else@gmail.com")
    assert other_response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unknown_email_also_blocked(client):
    for _ in range(rate_limit.MAX_FAILURES):
        wrong_login(client, "nobody@gmail.com")

    blocked_response = wrong_login(client, "nobody@gmail.com")
    assert blocked_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
