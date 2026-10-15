from fastapi import status


def refresh(client, token):
    return client.post("/auth/refresh", json={"refresh_token": token})


def logout(client, token):
    return client.post("/auth/logout", json={"refresh_token": token})


def test_logout_revokes_token(client, login_tokens):
    logout_response = logout(client, login_tokens["refresh_token"])
    assert logout_response.status_code == status.HTTP_204_NO_CONTENT

    refresh_response = refresh(client, login_tokens["refresh_token"])
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_revokes_whole_family(client, login_tokens):
    refresh_response = refresh(client, login_tokens["refresh_token"])
    assert refresh_response.status_code == status.HTTP_200_OK
    new_token = refresh_response.json()["refresh_token"]

    logout_response = logout(client, login_tokens["refresh_token"])
    assert logout_response.status_code == status.HTTP_204_NO_CONTENT

    assert refresh(client, new_token).status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_unknown_token(client):
    logout_response = logout(client, "fake-token")
    assert logout_response.status_code == status.HTTP_204_NO_CONTENT


def test_logout_keeps_other_sessions(client, registered_user):
    first = client.post("/auth/login", json=registered_user).json()
    second = client.post("/auth/login", json=registered_user).json()

    logout(client, first["refresh_token"])

    assert refresh(client, first["refresh_token"]).status_code == status.HTTP_401_UNAUTHORIZED
    assert refresh(client, second["refresh_token"]).status_code == status.HTTP_200_OK
