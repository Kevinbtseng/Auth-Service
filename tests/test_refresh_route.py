from fastapi import status
from app.database import SessionLocal
from app import models

def test_successful_refresh(client, registered_user):
    login_response = client.post("/auth/login", json=registered_user)
    assert login_response.status_code ==  status.HTTP_200_OK

    login_json = login_response.json()

    refresh_response = client.post("/auth/refresh", json={"refresh_token": login_json["refresh_token"]})
    assert refresh_response.status_code == status.HTTP_200_OK

    refresh_json = refresh_response.json()

    assert refresh_json["refresh_token"] != login_json["refresh_token"]
    assert refresh_json["access_token"]

def test_reused_token(client, registered_user):
    login_response = client.post("/auth/login", json=registered_user)
    assert login_response.status_code ==  status.HTTP_200_OK

    login_json = login_response.json()

    refresh_response = client.post("/auth/refresh", json={"refresh_token": login_json["refresh_token"]})
    assert refresh_response.status_code == status.HTTP_200_OK

    reused_response = client.post("/auth/refresh", json={"refresh_token": login_json["refresh_token"]})
    assert reused_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert reused_response.json()["detail"] == "Invalid or expired refresh token"

def test_family_revocation(client, login_tokens):
    login_json = login_tokens

    refresh_response = client.post("/auth/refresh", json={"refresh_token": login_json["refresh_token"]})
    assert refresh_response.status_code == status.HTTP_200_OK

    refresh_json = refresh_response.json()

    reused_response = client.post("/auth/refresh", json={"refresh_token": login_json["refresh_token"]})
    assert reused_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert reused_response.json()["detail"] == "Invalid or expired refresh token"

    revoked_response = client.post("/auth/refresh", json={"refresh_token": refresh_json["refresh_token"]})
    assert revoked_response.status_code == status.HTTP_401_UNAUTHORIZED

def test_unknown_token(client):
    refresh_response = client.post("/auth/refresh", json={"refresh_token": "fake-token"})
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert refresh_response.json()["detail"] == "Invalid or expired refresh token"

def test_deleted_user(client, login_tokens):
    with SessionLocal() as db:
        db.query(models.User).delete()
        db.commit()

    login_json = login_tokens

    refresh_response = client.post("/auth/refresh", json={"refresh_token": login_json["refresh_token"]})
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED